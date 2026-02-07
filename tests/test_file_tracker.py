"""
FileTracker 테스트 모듈.

MD5 해시 기반 파일 변경 감지 로직을 테스트합니다.
"""

import pytest
import tempfile
import json
from pathlib import Path
from synapse.file_tracker import FileTracker, FileState, ChangeSet


class TestFileState:
    """FileState 데이터 클래스 테스트"""
    
    def test_to_dict(self):
        state = FileState(
            path="/test/file.py",
            hash="abc123",
            mtime=1234567890.0,
            size=100
        )
        d = state.to_dict()
        
        assert d["path"] == "/test/file.py"
        assert d["hash"] == "abc123"
        assert d["mtime"] == 1234567890.0
        assert d["size"] == 100
    
    def test_from_dict(self):
        data = {
            "path": "/test/file.py",
            "hash": "abc123",
            "mtime": 1234567890.0,
            "size": 100
        }
        state = FileState.from_dict(data)
        
        assert state.path == "/test/file.py"
        assert state.hash == "abc123"


class TestChangeSet:
    """ChangeSet 데이터 클래스 테스트"""
    
    def test_has_changes_true(self):
        cs = ChangeSet(added=["a.py"], modified=[], deleted=[], unchanged=[])
        assert cs.has_changes is True
    
    def test_has_changes_false(self):
        cs = ChangeSet(added=[], modified=[], deleted=[], unchanged=["a.py"])
        assert cs.has_changes is False
    
    def test_total_changed(self):
        cs = ChangeSet(
            added=["a.py", "b.py"],
            modified=["c.py"],
            deleted=["d.py"],
            unchanged=["e.py"]
        )
        assert cs.total_changed == 4  # 2 + 1 + 1


class TestFileTracker:
    """FileTracker 클래스 테스트"""
    
    @pytest.fixture
    def temp_dir(self):
        """임시 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def tracker(self, temp_dir):
        """FileTracker 인스턴스 생성"""
        synapse_dir = temp_dir / ".synapse"
        synapse_dir.mkdir()
        return FileTracker(synapse_dir)
    
    def test_compute_hash(self, temp_dir):
        """해시 계산 테스트"""
        test_file = temp_dir / "test.py"
        test_file.write_text("print('hello')")
        
        hash1 = FileTracker.compute_hash(test_file)
        assert len(hash1) == 32  # MD5는 32자리 hex
        
        # 같은 내용은 같은 해시
        hash2 = FileTracker.compute_hash(test_file)
        assert hash1 == hash2
    
    def test_compute_hash_different_content(self, temp_dir):
        """다른 내용은 다른 해시"""
        file1 = temp_dir / "file1.py"
        file2 = temp_dir / "file2.py"
        
        file1.write_text("content1")
        file2.write_text("content2")
        
        assert FileTracker.compute_hash(file1) != FileTracker.compute_hash(file2)
    
    def test_get_changes_added(self, tracker, temp_dir):
        """새 파일 추가 감지"""
        # 파일 생성
        new_file = temp_dir / "new.py"
        new_file.write_text("print('new')")
        
        changes = tracker.get_changes([new_file])
        
        assert len(changes.added) == 1
        assert str(new_file) in changes.added
        assert len(changes.modified) == 0
        assert len(changes.deleted) == 0
    
    def test_get_changes_modified(self, tracker, temp_dir):
        """파일 수정 감지"""
        test_file = temp_dir / "test.py"
        test_file.write_text("version1")
        
        # 첫 번째 상태 저장
        tracker.update(test_file)
        tracker.save()
        
        # 파일 수정
        test_file.write_text("version2")
        
        changes = tracker.get_changes([test_file])
        
        assert len(changes.modified) == 1
        assert str(test_file) in changes.modified
    
    def test_get_changes_deleted(self, tracker, temp_dir):
        """파일 삭제 감지"""
        test_file = temp_dir / "test.py"
        test_file.write_text("content")
        
        # 상태 저장
        tracker.update(test_file)
        tracker.save()
        
        # 파일 삭제 후 빈 목록으로 검사
        test_file.unlink()
        
        changes = tracker.get_changes([])
        
        assert len(changes.deleted) == 1
        assert str(test_file) in changes.deleted
    
    def test_save_and_load(self, temp_dir):
        """저장 및 로드 테스트"""
        synapse_dir = temp_dir / ".synapse"
        synapse_dir.mkdir()
        
        # 트래커 1: 상태 저장
        tracker1 = FileTracker(synapse_dir)
        test_file = temp_dir / "test.py"
        test_file.write_text("content")
        tracker1.update(test_file)
        tracker1.save()
        
        # 트래커 2: 상태 로드
        tracker2 = FileTracker(synapse_dir)
        
        assert str(test_file) in tracker2.states
        assert tracker2.states[str(test_file)].hash == tracker1.states[str(test_file)].hash
    
    def test_clear(self, tracker, temp_dir):
        """상태 초기화 테스트"""
        test_file = temp_dir / "test.py"
        test_file.write_text("content")
        
        tracker.update(test_file)
        assert len(tracker.states) == 1
        
        tracker.clear()
        assert len(tracker.states) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
