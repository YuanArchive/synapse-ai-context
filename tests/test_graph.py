"""
Graph 테스트 모듈.

CodeGraph 의존성 그래프 로직을 테스트합니다.
"""

import pytest
import tempfile
from pathlib import Path
from synapse.graph import CodeGraph


class TestCodeGraph:
    """CodeGraph 클래스 테스트"""
    
    @pytest.fixture
    def temp_dir(self):
        """임시 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def graph(self, temp_dir):
        """CodeGraph 인스턴스 생성"""
        return CodeGraph(storage_path=temp_dir / "graph.gml")
    
    def test_add_file(self, graph):
        """파일 노드 추가"""
        graph.add_file("/src/main.py", language="python")
        
        assert "/src/main.py" in graph.graph.nodes
        assert graph.graph.nodes["/src/main.py"]["type"] == "file"
        assert graph.graph.nodes["/src/main.py"]["language"] == "python"
    
    def test_add_definition(self, graph):
        """정의 노드 추가 및 인덱싱"""
        graph.add_file("/src/main.py", language="python")
        graph.add_definition("my_function", "/src/main.py")
        
        # 심볼 노드 생성 확인
        assert "symbol:my_function" in graph.graph.nodes
        
        # 인덱스 확인
        assert "my_function" in graph.definition_index
        assert "/src/main.py" in graph.definition_index["my_function"]
    
    def test_add_call(self, graph):
        """호출 정보 추가"""
        graph.add_file("/src/main.py", language="python")
        graph.add_call("/src/main.py", "helper_func")
        
        calls = graph.graph.nodes["/src/main.py"].get("calls", [])
        assert "helper_func" in calls
    
    def test_resolve_references(self, graph):
        """참조 해석 (caller -> callee 엣지 생성)"""
        # 파일 추가
        graph.add_file("/src/main.py", language="python")
        graph.add_file("/src/utils.py", language="python")
        
        # utils.py에 helper 정의
        graph.add_definition("helper", "/src/utils.py")
        
        # main.py에서 helper 호출
        graph.add_call("/src/main.py", "helper")
        
        # 참조 해석
        graph.resolve_references()
        
        # main.py -> utils.py 엣지 확인
        assert graph.graph.has_edge("/src/main.py", "/src/utils.py")
    
    def test_get_related_files(self, graph):
        """관련 파일 탐색"""
        # 3개 파일 체인: A -> B -> C
        graph.add_file("/a.py", language="python")
        graph.add_file("/b.py", language="python")
        graph.add_file("/c.py", language="python")
        
        graph.add_definition("func_b", "/b.py")
        graph.add_definition("func_c", "/c.py")
        
        graph.add_call("/a.py", "func_b")
        graph.add_call("/b.py", "func_c")
        
        graph.resolve_references()
        
        # depth=1: 직접 연결만
        related = graph.get_related_files("/a.py", depth=1)
        assert "/b.py" in related
        
        # depth=2: 간접 연결도 포함
        related = graph.get_related_files("/a.py", depth=2)
        assert "/b.py" in related
    
    def test_save_and_load(self, graph, temp_dir):
        """저장 및 로드"""
        graph.add_file("/src/main.py", language="python")
        graph.add_definition("main", "/src/main.py")
        graph.save()
        
        # 새 그래프 인스턴스에서 로드
        graph2 = CodeGraph(storage_path=temp_dir / "graph.gml")
        graph2.load()
        
        assert "/src/main.py" in graph2.graph.nodes
        assert "main" in graph2.definition_index
    
    def test_empty_graph(self, graph):
        """빈 그래프 처리"""
        related = graph.get_related_files("/nonexistent.py")
        assert related == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
