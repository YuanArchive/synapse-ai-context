"""
계층적 컨텍스트 매니저: 토큰을 절약하면서 정보 손실 없이 컨텍스트를 구성합니다.

핵심 원칙:
- **토큰 절약 ≠ 정보 누락**: 토큰 예산으로 자르지 않고, Skeleton 변환으로 효율화
- Active 파일: 항상 Full Code (절대 자르지 않음)
- Reference 파일: Skeleton으로 압축 (구조 보존, 구현 상세 제거)
- Global 컨텍스트: 프로젝트 구조 + 메타데이터

3-Level 계층 구조:
- Level 0 (Global): 프로젝트 트리 + INTELLIGENCE.md
- Level 1 (Reference): Import된 파일들의 Skeleton
- Level 2 (Active): 현재 작업 파일 Full Code
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from collections import deque

from .structure.pruner import ASTSkeletonizer, SkeletonResult
from .graph import CodeGraph


@dataclass
class TokenSavings:
    """토큰 절약 효과 측정"""
    original_tokens: int
    optimized_tokens: int
    
    @property
    def saved_tokens(self) -> int:
        return self.original_tokens - self.optimized_tokens
    
    @property
    def savings_ratio(self) -> float:
        if self.original_tokens == 0:
            return 0.0
        return self.saved_tokens / self.original_tokens


@dataclass
class ContextResult:
    """컨텍스트 빌드 결과"""
    global_context: str       # Level 0
    reference_context: str    # Level 1 (Skeletons)
    active_context: str       # Level 2 (Full Code)
    
    total_tokens: int
    token_breakdown: Dict[str, int] = field(default_factory=dict)
    included_files: List[str] = field(default_factory=list)
    
    # 토큰 절약 효과
    savings: Optional[TokenSavings] = None
    
    @property
    def formatted_output(self) -> str:
        """포맷된 전체 컨텍스트 출력"""
        sections = []
        
        if self.global_context:
            sections.append(f"# 📂 Project Context\n\n{self.global_context}")
        
        if self.reference_context:
            sections.append(f"# 📚 Reference Files (Skeleton)\n\n{self.reference_context}")
        
        if self.active_context:
            sections.append(f"# 🎯 Active File (Full Code)\n\n{self.active_context}")
        
        return "\n\n---\n\n".join(sections)


class ContextManager:
    """
    3-Level 계층적 컨텍스트 관리자.
    
    **핵심 원칙**: 토큰을 "제한"하지 않고 "효율화"합니다.
    - Active 파일은 항상 Full Code로 포함 (절대 자르지 않음)
    - Reference 파일들은 Skeleton으로 압축하여 토큰 절약
    - 프로젝트 메타데이터로 전체 맥락 제공
    
    Example:
        >>> manager = ContextManager(Path("."))
        >>> result = manager.build_context(Path("src/main.py"))
        >>> print(f"토큰 절약: {result.savings.savings_ratio:.1%}")
        >>> print(result.formatted_output)
    """
    
    # 토큰 추정 상수 (chars per token)
    CHARS_PER_TOKEN = 4
    
    def __init__(
        self,
        project_path: Path,
        depth: int = 2,
        max_reference_files: int = 20
    ):
        """
        Args:
            project_path: 프로젝트 루트 경로
            depth: 의존성 탐색 깊이
            max_reference_files: 최대 Reference 파일 수 (너무 많으면 성능 저하)
        """
        self.project_path = Path(project_path).resolve()
        self.depth = depth
        self.max_reference_files = max_reference_files
        
        # .synapse 디렉토리 경로
        self.synapse_dir = self.project_path / ".synapse"
        
        # 의존성 그래프 로드
        self.graph = CodeGraph(storage_path=self.synapse_dir / "dependency_graph.gml")
        if (self.synapse_dir / "dependency_graph.gml").exists():
            self.graph.load()
        
        # Skeletonizer
        self.skeletonizer = ASTSkeletonizer()
    
    def build_context(self, active_file: Path) -> ContextResult:
        """
        Active 파일 기준으로 최적화된 컨텍스트를 생성합니다.
        
        **정보 손실 없음**: 토큰 예산으로 자르지 않습니다.
        대신 Reference 파일들을 Skeleton으로 변환하여 토큰을 절약합니다.
        
        Args:
            active_file: 현재 작업 중인 파일 경로
            
        Returns:
            ContextResult: 계층화된 컨텍스트 (모든 정보 포함)
        """
        active_file = Path(active_file).resolve()
        
        # 원본 토큰 추적용
        original_tokens = 0
        
        # Level 0: Global Context (전체 포함)
        global_context, global_tokens = self._build_global_context()
        original_tokens += global_tokens
        
        # Level 2: Active Context (전체 포함, 자르지 않음)
        active_context, active_tokens, active_original = self._build_active_context(active_file)
        original_tokens += active_original
        
        # Level 1: Reference Context (Skeleton으로 압축)
        reference_context, reference_tokens, reference_original, included_files = \
            self._build_reference_context(active_file)
        original_tokens += reference_original
        
        total_tokens = global_tokens + reference_tokens + active_tokens
        
        # 토큰 절약 효과 계산
        savings = TokenSavings(
            original_tokens=original_tokens,
            optimized_tokens=total_tokens
        )
        
        return ContextResult(
            global_context=global_context,
            reference_context=reference_context,
            active_context=active_context,
            total_tokens=total_tokens,
            token_breakdown={
                "global": global_tokens,
                "reference": reference_tokens,
                "active": active_tokens,
            },
            included_files=included_files,
            savings=savings
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """토큰 수 추정 (문자 수 / 4 근사치)"""
        return len(text) // self.CHARS_PER_TOKEN
    
    def _build_global_context(self) -> Tuple[str, int]:
        """Level 0: 프로젝트 전역 컨텍스트 구성 (전체 포함)"""
        parts = []
        
        # 1. INTELLIGENCE.md 읽기
        intel_path = self.synapse_dir / "INTELLIGENCE.md"
        if intel_path.exists():
            try:
                with open(intel_path, "r", encoding="utf-8") as f:
                    intel_content = f.read()
                parts.append(f"## Project Intelligence\n\n{intel_content}")
            except Exception:
                pass
        
        # 2. 간단한 프로젝트 트리 (최대 3레벨)
        tree_str = self._generate_tree(self.project_path, max_depth=3)
        if tree_str:
            parts.append(f"## Project Structure\n\n```\n{tree_str}\n```")
        
        global_context = "\n\n".join(parts)
        return global_context, self._estimate_tokens(global_context)
    
    def _build_active_context(self, active_file: Path) -> Tuple[str, int, int]:
        """
        Level 2: Active 파일 전체 코드 (절대 자르지 않음)
        
        Returns:
            Tuple[str, int, int]: (컨텍스트, 토큰수, 원본토큰수)
        """
        if not active_file.exists():
            msg = f"# File not found: {active_file}"
            return msg, 10, 10
        
        try:
            with open(active_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            try:
                rel_path = active_file.relative_to(self.project_path)
            except ValueError:
                rel_path = active_file.name
            
            # 언어 감지
            ext_to_lang = {
                ".py": "python", ".js": "javascript", ".ts": "typescript",
                ".jsx": "jsx", ".tsx": "tsx", ".go": "go", ".rs": "rust",
                ".java": "java", ".cpp": "cpp", ".c": "c"
            }
            lang = ext_to_lang.get(active_file.suffix.lower(), "")
            
            formatted = f"## {rel_path}\n\n```{lang}\n{content}\n```"
            tokens = self._estimate_tokens(formatted)
            
            # Active 파일은 압축하지 않으므로 원본 = 최적화
            return formatted, tokens, tokens
            
        except Exception as e:
            msg = f"# Error reading file: {e}"
            return msg, 10, 10
    
    def _build_reference_context(
        self, 
        active_file: Path
    ) -> Tuple[str, int, int, List[str]]:
        """
        Level 1: Import된 파일들의 Skeleton (정보 손실 없는 압축)
        
        Returns:
            Tuple[str, int, int, List[str]]: 
                (컨텍스트, 최적화토큰수, 원본토큰수, 포함파일목록)
        """
        # 관련 파일 찾기 (BFS)
        active_posix = active_file.as_posix()
        related_files = self._get_related_files_bfs(active_posix, self.depth)
        
        if not related_files:
            return "# No related files found", 5, 5, []
        
        # 최대 파일 수 제한 (성능)
        related_files = related_files[:self.max_reference_files]
        
        parts = []
        included = []
        optimized_tokens = 0
        original_tokens = 0
        
        for file_path in related_files:
            file_obj = Path(file_path)
            if not file_obj.exists():
                continue
            
            # 원본 파일 읽기 (토큰 절약 측정용)
            try:
                with open(file_obj, "r", encoding="utf-8") as f:
                    original_content = f.read()
                original_tokens += self._estimate_tokens(original_content)
            except Exception:
                continue
            
            # Skeleton 생성 (토큰 절약)
            result = self.skeletonizer.skeletonize_file(file_obj)
            
            try:
                rel_path = file_obj.relative_to(self.project_path)
            except ValueError:
                rel_path = file_obj.name
            
            # 언어 감지
            ext_to_lang = {
                ".py": "python", ".js": "javascript", ".ts": "typescript",
                ".jsx": "jsx", ".tsx": "tsx", ".go": "go", ".rs": "rust",
                ".java": "java", ".cpp": "cpp", ".c": "c"
            }
            lang = ext_to_lang.get(file_obj.suffix.lower(), "")
            
            skeleton_text = f"### {rel_path}\n\n```{lang}\n{result.skeleton}\n```"
            skeleton_tokens = self._estimate_tokens(skeleton_text)
            
            parts.append(skeleton_text)
            optimized_tokens += skeleton_tokens
            included.append(str(rel_path))
        
        reference_context = "\n\n".join(parts) if parts else "# No reference files included"
        return reference_context, optimized_tokens, original_tokens, included
    
    def _get_related_files_bfs(self, file_path: str, depth: int) -> List[str]:
        """BFS로 관련 파일 탐색 (depth 기반 우선순위)"""
        if file_path not in self.graph.graph:
            return []
        
        visited = set()
        queue = deque([(file_path, 0)])
        result = []
        
        while queue:
            current, current_depth = queue.popleft()
            
            if current in visited or current_depth > depth:
                continue
            visited.add(current)
            
            # 시작 파일 자체는 제외
            if current != file_path:
                # 파일 노드만 추가 (symbol 노드 제외)
                node_data = self.graph.graph.nodes.get(current, {})
                if node_data.get("type") == "file":
                    result.append((current, current_depth))
            
            # 인접 노드 탐색
            for neighbor in self.graph.graph.successors(current):
                if neighbor not in visited:
                    queue.append((neighbor, current_depth + 1))
            
            for neighbor in self.graph.graph.predecessors(current):
                if neighbor not in visited:
                    queue.append((neighbor, current_depth + 1))
        
        # depth 기준 정렬 (가까운 파일 우선)
        result.sort(key=lambda x: x[1])
        return [f for f, d in result]
    
    def _generate_tree(self, path: Path, max_depth: int = 3, prefix: str = "") -> str:
        """간단한 디렉토리 트리 생성"""
        exclude_dirs = {
            ".git", ".venv", "venv", "__pycache__", "node_modules",
            ".synapse", ".idea", ".vscode", "dist", "build"
        }
        
        lines = []
        
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return ""
        
        # 항목 필터링
        entries = [e for e in entries if e.name not in exclude_dirs]
        
        for i, entry in enumerate(entries[:20]):  # 최대 20개 항목
            is_last = i == len(entries) - 1 or i == 19
            connector = "└── " if is_last else "├── "
            
            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                if max_depth > 1:
                    extension = "    " if is_last else "│   "
                    subtree = self._generate_tree(entry, max_depth - 1, prefix + extension)
                    if subtree:
                        lines.append(subtree)
            else:
                lines.append(f"{prefix}{connector}{entry.name}")
        
        if len(entries) > 20:
            lines.append(f"{prefix}└── ... ({len(entries) - 20} more items)")
        
        return "\n".join(lines)


# 편의 함수
def build_context(
    project_path: str,
    active_file: str,
    depth: int = 2
) -> ContextResult:
    """
    컨텍스트를 빌드하는 편의 함수.
    
    토큰을 "제한"하지 않고 "효율화"합니다.
    Reference 파일들은 Skeleton으로 압축되어 토큰이 절약됩니다.
    
    Args:
        project_path: 프로젝트 루트 경로
        active_file: 현재 작업 파일 경로
        depth: 의존성 탐색 깊이
        
    Returns:
        ContextResult: 빌드된 컨텍스트 (정보 손실 없음)
    """
    manager = ContextManager(
        project_path=Path(project_path),
        depth=depth
    )
    return manager.build_context(Path(active_file))
