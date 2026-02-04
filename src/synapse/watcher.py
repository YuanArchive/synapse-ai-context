"""
File Watcher: 실시간 파일 변경 감시 데몬.

watchdog 라이브러리를 사용하여 파일 변경을 감지하고,
debounce 로직으로 과도한 업데이트를 방지하며 증분 인덱싱을 트리거합니다.
"""

import time
import threading
import json
from pathlib import Path
from typing import Set, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, field

try:
    from watchdog.observers import Observer
    from watchdog.events import (
        FileSystemEventHandler,
        FileCreatedEvent,
        FileModifiedEvent,
        FileDeletedEvent,
        FileMovedEvent,
    )
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object


@dataclass
class WatcherStatus:
    """Watcher 상태 정보"""
    running: bool
    pid: Optional[int]
    project_path: str
    started_at: Optional[str]
    events_processed: int = 0
    last_update: Optional[str] = None
    
    def to_dict(self):
        return {
            "running": self.running,
            "pid": self.pid,
            "project_path": self.project_path,
            "started_at": self.started_at,
            "events_processed": self.events_processed,
            "last_update": self.last_update,
        }


class DebouncedHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """
    Debounce 로직이 적용된 파일 이벤트 핸들러.
    
    사용자의 타이핑이 멈춘 후 지정된 시간(기본 2초)이 지나면
    인덱싱을 트리거합니다.
    """
    
    # 지원하는 파일 확장자
    SUPPORTED_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx",
        ".go", ".rs", ".java", ".cpp", ".cc",
        ".c", ".h", ".hpp"
    }
    
    # 무시할 디렉토리
    IGNORE_DIRS = {
        ".git", ".venv", "venv", "env", "__pycache__",
        "node_modules", "dist", "build", ".synapse",
        ".idea", ".vscode", "site-packages"
    }
    
    def __init__(
        self,
        project_path: Path,
        debounce_seconds: float = 2.0,
        on_update: Optional[Callable[[Set[str]], None]] = None
    ):
        super().__init__()
        self.project_path = project_path
        self.debounce_seconds = debounce_seconds
        self.on_update = on_update
        
        self._pending_files: Set[str] = set()
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._events_processed = 0
        self._last_update: Optional[str] = None
    
    def _should_process(self, path: str) -> bool:
        """파일이 처리 대상인지 확인"""
        p = Path(path)
        
        # 확장자 필터
        if p.suffix not in self.SUPPORTED_EXTENSIONS:
            return False
        
        # 무시할 디렉토리 필터
        for part in p.parts:
            if part in self.IGNORE_DIRS:
                return False
        
        return True
    
    def _schedule_update(self, file_path: str):
        """Debounce된 업데이트 스케줄링"""
        with self._lock:
            self._pending_files.add(file_path)
            
            # 기존 타이머 취소
            if self._timer:
                self._timer.cancel()
            
            # 새 타이머 설정
            self._timer = threading.Timer(
                self.debounce_seconds,
                self._trigger_update
            )
            self._timer.start()
    
    def _trigger_update(self):
        """인덱싱 트리거"""
        with self._lock:
            if not self._pending_files:
                return
            
            files_to_update = self._pending_files.copy()
            self._pending_files.clear()
            self._events_processed += len(files_to_update)
            self._last_update = datetime.now().isoformat()
        
        if self.on_update:
            self.on_update(files_to_update)
    
    def on_created(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            self._schedule_update(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            self._schedule_update(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            self._schedule_update(event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            if self._should_process(event.src_path):
                self._schedule_update(event.src_path)
            if self._should_process(event.dest_path):
                self._schedule_update(event.dest_path)
    
    @property
    def events_processed(self) -> int:
        return self._events_processed
    
    @property
    def last_update(self) -> Optional[str]:
        return self._last_update


class SynapseWatcher:
    """
    Synapse File Watcher.
    
    백그라운드에서 파일 변경을 감시하고 자동으로 증분 인덱싱을 수행합니다.
    """
    
    STATUS_FILE = "watcher_status.json"
    
    def __init__(
        self,
        project_path: Path,
        debounce_seconds: float = 2.0,
        quiet: bool = False
    ):
        if not WATCHDOG_AVAILABLE:
            raise ImportError(
                "watchdog 패키지가 설치되지 않았습니다. "
                "'pip install watchdog'로 설치하세요."
            )
        
        self.project_path = Path(project_path).resolve()
        self.synapse_dir = self.project_path / ".synapse"
        self.status_file = self.synapse_dir / self.STATUS_FILE
        self.debounce_seconds = debounce_seconds
        self.quiet = quiet
        
        self._observer: Optional[Observer] = None
        self._handler: Optional[DebouncedHandler] = None
        self._running = False
        self._started_at: Optional[str] = None
    
    def _on_files_changed(self, changed_files: Set[str]):
        """파일 변경 시 증분 인덱싱 수행"""
        if not self.quiet:
            print(f"[Synapse Watcher] {len(changed_files)} file(s) changed, reindexing...")
        
        try:
            # 증분 분석 수행
            from .analyzer import ProjectAnalyzer
            analyzer = ProjectAnalyzer(str(self.project_path))
            result = analyzer.analyze_incremental(json_output=True)
            
            if not self.quiet:
                changed = result.get("changed_files", 0)
                unchanged = result.get("unchanged_files", 0)
                print(f"[Synapse Watcher] ✓ Updated: {changed} changed, {unchanged} unchanged")
            
            # 상태 업데이트
            self._save_status()
            
        except Exception as e:
            if not self.quiet:
                print(f"[Synapse Watcher] Error: {e}")
    
    def start(self):
        """Watcher 시작"""
        if self._running:
            return
        
        self.synapse_dir.mkdir(parents=True, exist_ok=True)
        
        self._handler = DebouncedHandler(
            project_path=self.project_path,
            debounce_seconds=self.debounce_seconds,
            on_update=self._on_files_changed
        )
        
        self._observer = Observer()
        self._observer.schedule(
            self._handler,
            str(self.project_path),
            recursive=True
        )
        
        self._observer.start()
        self._running = True
        self._started_at = datetime.now().isoformat()
        
        self._save_status()
        
        if not self.quiet:
            print(f"[Synapse Watcher] Started watching: {self.project_path}")
    
    def stop(self):
        """Watcher 중지"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        
        self._running = False
        self._remove_status()
        
        if not self.quiet:
            print("[Synapse Watcher] Stopped")
    
    def run_forever(self):
        """블로킹 모드로 실행 (Ctrl+C로 종료)"""
        self.start()
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def _save_status(self):
        """상태 파일 저장"""
        import os
        status = WatcherStatus(
            running=self._running,
            pid=os.getpid(),
            project_path=str(self.project_path),
            started_at=self._started_at,
            events_processed=self._handler.events_processed if self._handler else 0,
            last_update=self._handler.last_update if self._handler else None
        )
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status.to_dict(), f, indent=2)
    
    def _remove_status(self):
        """상태 파일 제거"""
        if self.status_file.exists():
            self.status_file.unlink()
    
    @classmethod
    def get_status(cls, project_path: Path) -> Optional[WatcherStatus]:
        """Watcher 상태 조회"""
        synapse_dir = Path(project_path).resolve() / ".synapse"
        status_file = synapse_dir / cls.STATUS_FILE
        
        if not status_file.exists():
            return WatcherStatus(
                running=False,
                pid=None,
                project_path=str(project_path),
                started_at=None
            )
        
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 프로세스가 실제로 실행 중인지 확인
            import os
            pid = data.get("pid")
            if pid:
                try:
                    os.kill(pid, 0)  # 시그널 0은 프로세스 존재 확인
                except (OSError, ProcessLookupError):
                    # 프로세스가 죽었음
                    return WatcherStatus(
                        running=False,
                        pid=None,
                        project_path=str(project_path),
                        started_at=None
                    )
            
            return WatcherStatus(
                running=data.get("running", False),
                pid=data.get("pid"),
                project_path=data.get("project_path", str(project_path)),
                started_at=data.get("started_at"),
                events_processed=data.get("events_processed", 0),
                last_update=data.get("last_update")
            )
        except (json.JSONDecodeError, KeyError):
            return WatcherStatus(
                running=False,
                pid=None,
                project_path=str(project_path),
                started_at=None
            )


def is_watchdog_available() -> bool:
    """watchdog 패키지 사용 가능 여부"""
    return WATCHDOG_AVAILABLE
