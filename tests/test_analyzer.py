"""
Analyzer 테스트 모듈.

ProjectAnalyzer 분석 엔진을 테스트합니다.
"""

import pytest
import tempfile
from pathlib import Path
from synapse.analyzer import ProjectAnalyzer


class TestProjectAnalyzer:
    """ProjectAnalyzer 클래스 테스트"""
    
    @pytest.fixture
    def temp_project(self):
        """임시 프로젝트 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # 샘플 Python 파일 생성
            src_dir = project / "src"
            src_dir.mkdir()
            
            main_py = src_dir / "main.py"
            main_py.write_text('''
def main():
    """메인 함수"""
    print("Hello")
    helper()

def helper():
    """헬퍼 함수"""
    return 42
''')
            
            utils_py = src_dir / "utils.py"
            utils_py.write_text('''
def calculate(a, b):
    """계산 함수"""
    return a + b

class Calculator:
    """계산기 클래스"""
    def add(self, a, b):
        return a + b
''')
            
            yield project
    
    @pytest.fixture
    def analyzer(self, temp_project):
        """ProjectAnalyzer 인스턴스 생성"""
        return ProjectAnalyzer(str(temp_project))
    
    def test_scan_files(self, analyzer):
        """파일 스캔 테스트"""
        files = analyzer.scan_files()
        
        # 2개의 .py 파일이 있어야 함
        assert len(files) == 2
        
        # 모두 .py 확장자
        for f in files:
            assert f.suffix == ".py"
    
    def test_scan_files_excludes(self, temp_project):
        """제외 디렉토리 테스트"""
        # __pycache__ 디렉토리 생성
        pycache = temp_project / "src" / "__pycache__"
        pycache.mkdir()
        (pycache / "module.pyc").write_text("bytecode")
        
        analyzer = ProjectAnalyzer(str(temp_project))
        files = analyzer.scan_files()
        
        # __pycache__ 파일은 제외
        for f in files:
            assert "__pycache__" not in str(f)
    
    def test_analyze_creates_synapse_dir(self, analyzer):
        """분석 시 .synapse 디렉토리 생성"""
        analyzer.analyze(json_output=True)
        
        assert analyzer.db_dir.exists()
        assert (analyzer.db_dir / "dependency_graph.gml").exists()
    
    def test_analyze_returns_summary(self, analyzer):
        """분석 결과 요약 반환"""
        result = analyzer.analyze(json_output=True)
        
        assert result["status"] == "success"
        assert result["files_analyzed"] == 2
        assert result["documents_indexed"] > 0
        assert result["graph_nodes"] > 0
    
    def test_analyze_incremental_first_run(self, analyzer):
        """증분 분석 첫 실행 (전체 분석)"""
        result = analyzer.analyze_incremental(json_output=True)
        
        assert result["status"] == "success"
        assert result["mode"] == "incremental"
        # 첫 실행이므로 모든 파일이 added
        assert result["added_files"] == 2
    
    def test_analyze_incremental_no_changes(self, analyzer, temp_project):
        """증분 분석 - 변경 없음"""
        # 첫 분석
        analyzer.analyze_incremental(json_output=True)
        
        # 새 analyzer로 재분석
        analyzer2 = ProjectAnalyzer(str(temp_project))
        result = analyzer2.analyze_incremental(json_output=True)
        
        assert result["changed_files"] == 0
        assert result["unchanged_files"] == 2
    
    def test_analyze_incremental_modified(self, analyzer, temp_project):
        """증분 분석 - 파일 수정 감지"""
        # 첫 분석
        analyzer.analyze_incremental(json_output=True)
        
        # 파일 수정
        main_py = temp_project / "src" / "main.py"
        main_py.write_text("# Modified\nprint('changed')")
        
        # 새 analyzer로 재분석
        analyzer2 = ProjectAnalyzer(str(temp_project))
        result = analyzer2.analyze_incremental(json_output=True)
        
        assert result["modified_files"] == 1
        assert result["unchanged_files"] == 1
    
    def test_nonexistent_path(self):
        """존재하지 않는 경로 처리"""
        analyzer = ProjectAnalyzer("/nonexistent/path")
        result = analyzer.analyze(json_output=True)
        
        assert result["status"] == "error"
        assert "does not exist" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
