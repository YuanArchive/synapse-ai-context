"""
File Tracker: 파일 변경 감지를 위한 해시 기반 트래커.

파일의 해시값을 저장하고 비교하여 변경/추가/삭제된 파일을 감지합니다.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class FileState:
    """파일 상태 정보"""
    path: str
    hash: str
    mtime: float
    size: int
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileState':
        return cls(**data)


@dataclass
class ChangeSet:
    """변경된 파일 집합"""
    added: List[str]      # 새로 추가된 파일
    modified: List[str]   # 수정된 파일
    deleted: List[str]    # 삭제된 파일
    unchanged: List[str]  # 변경 없는 파일
    
    @property
    def has_changes(self) -> bool:
        return len(self.added) > 0 or len(self.modified) > 0 or len(self.deleted) > 0
    
    @property
    def total_changed(self) -> int:
        return len(self.added) + len(self.modified) + len(self.deleted)


class FileTracker:
    """
    파일 변경 감지를 위한 해시 기반 트래커.
    
    .synapse/file_hashes.json에 파일별 해시와 메타데이터를 저장하고,
    현재 파일 상태와 비교하여 변경된 파일을 반환합니다.
    """
    
    HASH_FILE = "file_hashes.json"
    
    def __init__(self, synapse_dir: Path):
        """
        Args:
            synapse_dir: .synapse 디렉토리 경로
        """
        self.synapse_dir = Path(synapse_dir)
        self.hash_file = self.synapse_dir / self.HASH_FILE
        self.states: Dict[str, FileState] = {}
        self._load()
    
    def _load(self) -> None:
        """저장된 파일 상태 로드"""
        if self.hash_file.exists():
            try:
                with open(self.hash_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for path, state_dict in data.get('files', {}).items():
                        self.states[path] = FileState.from_dict(state_dict)
            except (json.JSONDecodeError, KeyError) as e:
                # 손상된 파일은 무시하고 새로 시작
                self.states = {}
    
    def save(self) -> None:
        """파일 상태 저장"""
        self.synapse_dir.mkdir(parents=True, exist_ok=True)
        data = {
            'version': '1.0',
            'updated_at': datetime.now().isoformat(),
            'files': {path: state.to_dict() for path, state in self.states.items()}
        }
        with open(self.hash_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def compute_hash(file_path: Path) -> str:
        """파일의 MD5 해시 계산"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                # 큰 파일을 위해 청크 단위로 읽기
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError):
            return ""
    
    def get_file_state(self, file_path: Path) -> Optional[FileState]:
        """파일의 현재 상태 가져오기"""
        if not file_path.exists():
            return None
        
        try:
            stat = file_path.stat()
            return FileState(
                path=str(file_path),
                hash=self.compute_hash(file_path),
                mtime=stat.st_mtime,
                size=stat.st_size
            )
        except (IOError, OSError):
            return None
    
    def get_changes(self, current_files: List[Path]) -> ChangeSet:
        """
        현재 파일 목록과 저장된 상태를 비교하여 변경 사항 반환.
        
        Args:
            current_files: 현재 프로젝트의 파일 목록
            
        Returns:
            ChangeSet: 추가/수정/삭제/변경없음 파일 목록
        """
        added: List[str] = []
        modified: List[str] = []
        unchanged: List[str] = []
        
        current_paths = {str(f) for f in current_files}
        stored_paths = set(self.states.keys())
        
        # 삭제된 파일: 저장되어 있지만 현재 없는 파일
        deleted = list(stored_paths - current_paths)
        
        for file_path in current_files:
            path_str = str(file_path)
            current_state = self.get_file_state(file_path)
            
            if current_state is None:
                continue
            
            if path_str not in self.states:
                # 새로 추가된 파일
                added.append(path_str)
            else:
                stored_state = self.states[path_str]
                # 해시 비교로 변경 감지
                if current_state.hash != stored_state.hash:
                    modified.append(path_str)
                else:
                    unchanged.append(path_str)
        
        return ChangeSet(
            added=added,
            modified=modified,
            deleted=deleted,
            unchanged=unchanged
        )
    
    def update(self, file_path: Path) -> None:
        """단일 파일 상태 업데이트"""
        state = self.get_file_state(file_path)
        if state:
            self.states[str(file_path)] = state
    
    def update_batch(self, file_paths: List[Path]) -> None:
        """여러 파일 상태 일괄 업데이트"""
        for file_path in file_paths:
            self.update(file_path)
    
    def remove(self, file_path: str) -> None:
        """파일 상태 제거 (삭제된 파일 처리)"""
        if file_path in self.states:
            del self.states[file_path]
    
    def clear(self) -> None:
        """모든 상태 초기화 (전체 재인덱싱 시 사용)"""
        self.states = {}
        if self.hash_file.exists():
            self.hash_file.unlink()
