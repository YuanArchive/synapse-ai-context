"""
Hybrid Search: Vector Search + Graph Traversal 결합 검색.

기존 Vector Search만으로는 의미적 유사성만 파악하고 구조적 관계를 모릅니다.
Graph RAG를 통해 "이 함수를 호출하는 파일", "이 함수가 사용하는 모듈" 등 
코드 구조 기반 컨텍스트를 함께 제공합니다.

Hybrid Retrieval Strategy:
1. Seed Discovery - Vector DB에서 Top-K 후보 추출
2. Graph Expansion - Seed 노드로부터 관련 노드 탐색
3. Hybrid Scoring - (Vector Score × α) + (Graph Score × β)
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import math

from .vector_store import VectorStore
from .graph import CodeGraph


@dataclass
class SearchResult:
    """검색 결과 항목"""
    node_id: str           # 파일 경로 또는 심볼 ID
    content: str           # 코드 내용
    vector_score: float    # Vector 유사도 점수 (0~1, 높을수록 유사)
    graph_score: float     # Graph 중심성 점수 (0~1)
    hybrid_score: float    # 최종 결합 점수
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Graph 관계 정보
    depth_from_seed: int = 0  # Seed로부터의 거리 (hop 수)
    relation_type: str = "direct"  # "direct" | "caller" | "callee"


@dataclass
class HybridSearchResult:
    """Hybrid Search 전체 결과"""
    query: str
    results: List[SearchResult]
    seeds_count: int        # 초기 Vector Search 결과 수
    expanded_count: int     # Graph 확장 후 결과 수
    
    def get_contexts(self) -> List[str]:
        """검색 결과의 코드 컨텍스트 목록 반환"""
        return [r.content for r in self.results]


class HybridSearch:
    """
    Vector Search + Graph Traversal 결합 검색 엔진.
    
    Example:
        >>> hybrid = HybridSearch(vector_store, code_graph)
        >>> results = hybrid.search("로그인 실패 처리", top_k=10)
        >>> for r in results.results:
        ...     print(f"{r.node_id}: {r.hybrid_score:.3f}")
    """
    
    # 가중치 상수
    DEFAULT_ALPHA = 0.7   # Vector Score 가중치
    DEFAULT_BETA = 0.3    # Graph Score 가중치
    
    # Graph 탐색 설정
    DEFAULT_EXPANSION_DEPTH = 2  # Seed로부터 탐색할 홉 수
    DEFAULT_MAX_EXPANDED = 30    # 최대 확장 노드 수
    
    def __init__(
        self,
        vector_store: VectorStore,
        graph: CodeGraph,
        alpha: float = DEFAULT_ALPHA,
        beta: float = DEFAULT_BETA
    ):
        """
        Args:
            vector_store: ChromaDB 벡터 스토어
            graph: 의존성 그래프
            alpha: Vector Score 가중치 (0~1)
            beta: Graph Score 가중치 (0~1)
        """
        self.vector_store = vector_store
        self.graph = graph
        self.alpha = alpha
        self.beta = beta
        
        # 검증: alpha + beta = 1
        if not math.isclose(alpha + beta, 1.0, rel_tol=1e-5):
            # 자동 정규화
            total = alpha + beta
            self.alpha = alpha / total
            self.beta = beta / total
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        expansion_depth: int = DEFAULT_EXPANSION_DEPTH
    ) -> HybridSearchResult:
        """
        Hybrid Retrieval 수행.
        
        Args:
            query: 검색 쿼리
            top_k: 최종 반환할 결과 수
            expansion_depth: Graph 탐색 깊이
            
        Returns:
            HybridSearchResult: 랭킹된 검색 결과
        """
        # Step 1: Seed Discovery (Vector Search)
        seeds = self._vector_search(query, n_results=top_k * 2)
        
        if not seeds:
            return HybridSearchResult(
                query=query,
                results=[],
                seeds_count=0,
                expanded_count=0
            )
        
        # Step 2: Graph Expansion
        expanded = self._expand_with_graph(seeds, depth=expansion_depth)
        
        # Step 3: Hybrid Scoring & Ranking
        ranked = self._rank_results(seeds, expanded)
        
        return HybridSearchResult(
            query=query,
            results=ranked[:top_k],
            seeds_count=len(seeds),
            expanded_count=len(expanded)
        )
    
    def _vector_search(self, query: str, n_results: int) -> List[SearchResult]:
        """Step 1: Vector DB에서 의미적으로 유사한 노드 검색"""
        try:
            results = self.vector_store.query(query, n_results=n_results)
        except Exception:
            return []
        
        if not results or not results.get("documents"):
            return []
        
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results.get("distances", [[0] * len(documents)])[0]
        ids = results.get("ids", [[]])[0]
        
        search_results = []
        for i, (doc, meta, dist, node_id) in enumerate(zip(documents, metadatas, distances, ids)):
            # ChromaDB distance를 score로 변환 (distance가 낮을수록 유사)
            # L2 distance 기준: score = 1 / (1 + distance)
            vector_score = 1.0 / (1.0 + dist)
            
            search_results.append(SearchResult(
                node_id=meta.get("path", node_id),
                content=doc,
                vector_score=vector_score,
                graph_score=0.0,  # 나중에 계산
                hybrid_score=0.0,  # 나중에 계산
                metadata=meta,
                depth_from_seed=0,
                relation_type="direct"
            ))
        
        return search_results
    
    def _expand_with_graph(
        self,
        seeds: List[SearchResult],
        depth: int
    ) -> List[SearchResult]:
        """
        Step 2: Seed 노드에서 Graph를 탐색하여 관련 노드 확장.
        
        - Callers (Upstream): 이 함수를 호출하는 곳 → 영향도 파악
        - Callees (Downstream): 이 함수가 사용하는 것 → 동작 원리 파악
        """
        if not seeds:
            return []
        
        expanded = []
        visited = set()
        
        # Seed 노드들의 ID 수집
        seed_ids = {s.node_id for s in seeds}
        visited.update(seed_ids)
        
        for seed in seeds:
            # BFS로 관련 노드 탐색
            queue = deque([(seed.node_id, 0, "seed")])
            
            while queue and len(expanded) < self.DEFAULT_MAX_EXPANDED:
                current, current_depth, relation = queue.popleft()
                
                if current_depth > depth:
                    continue
                
                # 그래프에서 인접 노드 탐색
                if current not in self.graph.graph:
                    continue
                
                # Callees (Downstream): 이 노드가 호출하는 것
                for callee in self.graph.graph.successors(current):
                    if callee in visited or callee.startswith("symbol:"):
                        continue
                    
                    node_data = self.graph.graph.nodes.get(callee, {})
                    if node_data.get("type") != "file":
                        continue
                    
                    visited.add(callee)
                    
                    # 파일 내용 읽기 시도
                    content = self._read_file_content(callee)
                    if content:
                        expanded.append(SearchResult(
                            node_id=callee,
                            content=content,
                            vector_score=0.0,  # Vector 검색 결과가 아님
                            graph_score=0.0,  # 나중에 계산
                            hybrid_score=0.0,
                            metadata={"path": callee, "source": "graph_expansion"},
                            depth_from_seed=current_depth + 1,
                            relation_type="callee"
                        ))
                        
                        if current_depth + 1 < depth:
                            queue.append((callee, current_depth + 1, "callee"))
                
                # Callers (Upstream): 이 노드를 호출하는 것
                for caller in self.graph.graph.predecessors(current):
                    if caller in visited or caller.startswith("symbol:"):
                        continue
                    
                    node_data = self.graph.graph.nodes.get(caller, {})
                    if node_data.get("type") != "file":
                        continue
                    
                    visited.add(caller)
                    
                    content = self._read_file_content(caller)
                    if content:
                        expanded.append(SearchResult(
                            node_id=caller,
                            content=content,
                            vector_score=0.0,
                            graph_score=0.0,
                            hybrid_score=0.0,
                            metadata={"path": caller, "source": "graph_expansion"},
                            depth_from_seed=current_depth + 1,
                            relation_type="caller"
                        ))
                        
                        if current_depth + 1 < depth:
                            queue.append((caller, current_depth + 1, "caller"))
        
        return expanded
    
    def _rank_results(
        self,
        seeds: List[SearchResult],
        expanded: List[SearchResult]
    ) -> List[SearchResult]:
        """
        Step 3: Hybrid Scoring으로 최종 랭킹.
        
        Score = (Vector Score × α) + (Graph Score × β)
        
        Graph Score 계산:
        - Depth 0 (Seed): 1.0
        - Depth 1: 0.7
        - Depth 2: 0.5
        - Caller 보너스: +0.1 (영향도가 높으므로)
        """
        all_results = []
        
        # Seeds 처리
        for seed in seeds:
            # Seed는 Graph Score 최대
            seed.graph_score = 1.0
            seed.hybrid_score = (self.alpha * seed.vector_score) + (self.beta * seed.graph_score)
            all_results.append(seed)
        
        # Expanded 처리
        for exp in expanded:
            # Depth 기반 Graph Score
            depth_scores = {0: 1.0, 1: 0.7, 2: 0.5}
            base_graph_score = depth_scores.get(exp.depth_from_seed, 0.3)
            
            # Caller 보너스 (이 코드에 영향을 주는 파일은 더 중요)
            if exp.relation_type == "caller":
                base_graph_score = min(1.0, base_graph_score + 0.1)
            
            exp.graph_score = base_graph_score
            
            # Vector Score가 없으므로 Graph Score만 사용
            # 또는 확장된 노드에 대해 별도 Vector 검색 수행 가능 (선택적)
            exp.hybrid_score = self.beta * exp.graph_score
            
            all_results.append(exp)
        
        # Hybrid Score 기준 내림차순 정렬
        all_results.sort(key=lambda x: x.hybrid_score, reverse=True)
        
        # 중복 제거 (같은 node_id가 여러 경로로 도달했을 수 있음)
        seen = set()
        unique_results = []
        for r in all_results:
            if r.node_id not in seen:
                seen.add(r.node_id)
                unique_results.append(r)
        
        return unique_results
    
    def _read_file_content(self, file_path: str) -> Optional[str]:
        """파일 내용 읽기 (Graph 확장 시 사용)"""
        try:
            from pathlib import Path
            path = Path(file_path)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception:
            pass
        return None


# 편의 함수
def hybrid_search(
    query: str,
    vector_store: VectorStore,
    graph: CodeGraph,
    top_k: int = 10
) -> HybridSearchResult:
    """
    Hybrid Search 수행 편의 함수.
    
    Args:
        query: 검색 쿼리
        vector_store: Vector Store 인스턴스
        graph: CodeGraph 인스턴스
        top_k: 반환할 결과 수
        
    Returns:
        HybridSearchResult: 검색 결과
    """
    searcher = HybridSearch(vector_store, graph)
    return searcher.search(query, top_k=top_k)
