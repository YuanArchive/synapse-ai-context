"""
AST Skeletonizer: 코드의 Skeleton(뼈대)을 추출하여 토큰 효율성을 극대화합니다.

PPL 기반 압축과 달리, AST를 분석하여 구조적으로 중요한 부분만 보존합니다:
- 함수/클래스 시그니처 + Docstring 유지
- 함수 Body는 `...` (Ellipsis)로 대체
- Import 문 유지
- 전역 변수/상수 유지
"""

import ast
from pathlib import Path
from typing import Optional, Union
from dataclasses import dataclass


@dataclass
class SkeletonResult:
    """Skeleton 변환 결과"""
    skeleton: str
    original_lines: int
    skeleton_lines: int
    reduction_ratio: float  # 0.0 ~ 1.0


class ASTSkeletonizer:
    """
    소스 코드를 AST로 파싱하여 Skeleton을 생성합니다.
    
    Skeleton은 다음을 포함합니다:
    - 모든 Import 문
    - 클래스/함수 시그니처 (def, class 라인)
    - Docstring (첫 번째 문자열 리터럴)
    - 전역 변수 할당
    - 타입 힌트
    
    Skeleton에서 제거되는 것:
    - 함수/메서드 Body (... 로 대체)
    - 인라인 주석 (#)
    - 구현 상세 로직
    """
    
    def __init__(self, preserve_comments: bool = False):
        """
        Args:
            preserve_comments: True면 인라인 주석도 보존 (기본값: False)
        """
        self.preserve_comments = preserve_comments
    
    def skeletonize(self, source_code: str, language: str = "python") -> SkeletonResult:
        """
        원본 코드를 Skeleton으로 변환합니다.
        
        Args:
            source_code: 원본 소스 코드
            language: 프로그래밍 언어 (현재 python만 지원)
            
        Returns:
            SkeletonResult: 변환 결과
        """
        if language.lower() != "python":
            # Python 외 언어는 추후 tree-sitter로 확장
            return SkeletonResult(
                skeleton=source_code,
                original_lines=source_code.count("\n") + 1,
                skeleton_lines=source_code.count("\n") + 1,
                reduction_ratio=0.0
            )
        
        return self._skeletonize_python(source_code)
    
    def skeletonize_file(self, file_path: Path) -> SkeletonResult:
        """
        파일을 읽어서 Skeleton으로 변환합니다.
        
        Args:
            file_path: 소스 파일 경로
            
        Returns:
            SkeletonResult: 변환 결과
        """
        file_path = Path(file_path)
        
        # 언어 감지
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
        }
        language = ext_to_lang.get(file_path.suffix.lower(), "unknown")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            return self.skeletonize(source_code, language)
        except Exception as e:
            # 파일 읽기 실패 시 빈 결과 반환
            return SkeletonResult(
                skeleton=f"# Error reading file: {e}",
                original_lines=0,
                skeleton_lines=1,
                reduction_ratio=0.0
            )
    
    def _skeletonize_python(self, source_code: str) -> SkeletonResult:
        """Python 코드 Skeleton 변환 (ast 모듈 사용)"""
        original_lines = source_code.count("\n") + 1
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            # 파싱 실패 시 원본 반환
            return SkeletonResult(
                skeleton=f"# SyntaxError: {e}\n{source_code}",
                original_lines=original_lines,
                skeleton_lines=original_lines + 1,
                reduction_ratio=0.0
            )
        
        # AST 변환
        transformer = _SkeletonTransformer()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        
        # AST를 소스 코드로 변환 (Python 3.9+)
        try:
            skeleton = ast.unparse(new_tree)
        except Exception:
            # unparse 실패 시 수동 구성
            skeleton = self._manual_skeleton_build(tree, source_code)
        
        skeleton_lines = skeleton.count("\n") + 1
        reduction = 1.0 - (skeleton_lines / original_lines) if original_lines > 0 else 0.0
        
        return SkeletonResult(
            skeleton=skeleton,
            original_lines=original_lines,
            skeleton_lines=skeleton_lines,
            reduction_ratio=max(0.0, reduction)
        )
    
    def _manual_skeleton_build(self, tree: ast.Module, source_code: str) -> str:
        """
        ast.unparse가 실패할 경우의 폴백 메서드.
        원본 소스에서 필요한 라인만 추출합니다.
        """
        lines = source_code.split("\n")
        keep_lines = set()
        
        for node in ast.walk(tree):
            # Import 문
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if hasattr(node, "lineno"):
                    keep_lines.add(node.lineno - 1)
            
            # 함수/클래스 정의
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if hasattr(node, "lineno"):
                    keep_lines.add(node.lineno - 1)
                    
                    # Docstring 추출
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                # Docstring 라인들 추가
                                doc_start = node.body[0].lineno - 1
                                doc_end = node.body[0].end_lineno
                                for i in range(doc_start, doc_end):
                                    keep_lines.add(i)
            
            # 전역 할당
            elif isinstance(node, ast.Assign):
                # 함수/클래스 외부의 할당만
                if hasattr(node, "lineno"):
                    keep_lines.add(node.lineno - 1)
        
        result_lines = []
        for i in sorted(keep_lines):
            if i < len(lines):
                result_lines.append(lines[i])
        
        return "\n".join(result_lines)


class _SkeletonTransformer(ast.NodeTransformer):
    """
    AST를 순회하며 함수/메서드 Body를 Ellipsis(...)로 대체합니다.
    """
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """함수 정의 변환"""
        return self._transform_function(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """비동기 함수 정의 변환"""
        return self._transform_function(node)
    
    def _transform_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]):
        """함수 Body를 Docstring + Ellipsis로 대체"""
        new_body = []
        
        # Docstring 보존 (첫 번째 Expr이 문자열인 경우)
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant):
                if isinstance(node.body[0].value.value, str):
                    new_body.append(node.body[0])
        
        # Ellipsis 추가
        ellipsis_node = ast.Expr(value=ast.Constant(value=...))
        new_body.append(ellipsis_node)
        
        # 새로운 body로 교체
        node.body = new_body
        
        # 중첩 클래스/함수는 재귀적으로 처리하지 않음 (이미 제거됨)
        return node
    
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """클래스 정의 변환 - 메서드들의 Body만 축소"""
        new_body = []
        
        # Docstring 보존
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant):
                if isinstance(node.body[0].value.value, str):
                    new_body.append(node.body[0])
        
        # 메서드와 클래스 변수만 유지
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 메서드는 재귀적으로 변환
                transformed = self.visit(item)
                new_body.append(transformed)
            elif isinstance(item, ast.Assign):
                # 클래스 변수 유지
                new_body.append(item)
            elif isinstance(item, ast.AnnAssign):
                # 타입 힌트가 있는 클래스 변수 유지
                new_body.append(item)
            elif isinstance(item, ast.ClassDef):
                # 중첩 클래스도 재귀적으로 변환
                transformed = self.visit(item)
                new_body.append(transformed)
        
        # Body가 비어있으면 pass 추가
        if not new_body:
            new_body.append(ast.Pass())
        
        node.body = new_body
        return node


# 편의 함수
def skeletonize(source_code: str, language: str = "python") -> str:
    """
    소스 코드를 Skeleton으로 변환하는 편의 함수.
    
    Args:
        source_code: 원본 소스 코드
        language: 프로그래밍 언어
        
    Returns:
        str: Skeleton 코드
    """
    skeletonizer = ASTSkeletonizer()
    result = skeletonizer.skeletonize(source_code, language)
    return result.skeleton


def skeletonize_file(file_path: Union[str, Path]) -> str:
    """
    파일을 Skeleton으로 변환하는 편의 함수.
    
    Args:
        file_path: 소스 파일 경로
        
    Returns:
        str: Skeleton 코드
    """
    skeletonizer = ASTSkeletonizer()
    result = skeletonizer.skeletonize_file(Path(file_path))
    return result.skeleton
