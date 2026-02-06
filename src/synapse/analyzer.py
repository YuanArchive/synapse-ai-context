from pathlib import Path
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

from .parser import CodeParser
from .vector_store import VectorStore
from .graph import CodeGraph
from .file_tracker import FileTracker, ChangeSet
from .exceptions import SynapseError, IndexingError, ParserError
from .logger import get_logger
import networkx as nx


class ProjectAnalyzer:
    """
    Project Analysis Engine.
    Scans the codebase, orchestrates parsing, builds semantic index AND dependency graph.
    """

    def __init__(self, project_path: str, exclude_dirs: Optional[List[str]] = None):
        self.project_path = Path(project_path).resolve()
        self.exclude_dirs = exclude_dirs or [
            ".git",
            ".venv",
            ".venv_old",
            "venv",
            "env",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
            ".synapse",
            ".idea",
            ".vscode",
            "site-packages",
        ]
        self.parser = CodeParser()
        # Store DB inside a hidden .synapse folder in the target project
        self.db_dir = self.project_path / ".synapse"
        
        # 경로가 존재할 때만 .synapse 디렉토리 생성 및 초기화
        if self.project_path.exists():
            self.db_dir.mkdir(exist_ok=True)
            self.vector_store = VectorStore(db_path=str(self.db_dir / "db"))
            # Initialize Dependency Graph
            self.code_graph = CodeGraph(storage_path=self.db_dir / "dependency_graph.gml")
        else:
            # 경로가 존재하지 않으면 나중에 analyze()에서 에러 처리
            self.vector_store = None
            self.code_graph = None
        self.results = []

    def scan_files(
        self,
        extensions: List[str] = [
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".go",
            ".rs",
            ".java",
            ".cpp",
            ".cc",
            ".c",
            ".h",
            ".hpp",
        ],
    ) -> List[Path]:
        """
        Recursively scan for supported code files.
        """
        files = []
        for path in self.project_path.rglob("*"):
            # Skip excluded directories
            if any(excluded in path.parts for excluded in self.exclude_dirs):
                continue

            if path.is_file() and path.suffix in extensions:
                files.append(path)
        return files

    def analyze(self, json_output: bool = False):
        """
        Main analysis pipeline.
        """
        if not self.project_path.exists():
            error_msg = f"Path {self.project_path} does not exist."
            if json_output:
                return {"status": "error", "message": error_msg}
            console.print(f"[bold red]Error:[/bold red] {error_msg}")
            return

        files = self.scan_files()
        if not json_output:
            console.print(
                f"[bold blue]Analyzing {len(files)} files with Tree-sitter...[/bold blue]"
            )

        documents = []
        metadatas = []
        ids = []

        if json_output:
            # Non-interactive mode
            for file_path in files:
                self._process_file(file_path, documents, metadatas, ids)
        else:
            # Interactive mode with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Parsing & Indexing...", total=len(files))

                for file_path in files:
                    self._process_file(file_path, documents, metadatas, ids)
                    progress.advance(task)

        # 4. Batch Insert into ChromaDB
        if documents:
            if not json_output:
                console.print(f"[blue]Embedding {len(documents)} documents...[/blue]")
            self.vector_store.add_documents(
                documents, metadatas, ids, quiet=json_output
            )

        # 5. Build and Save Graph
        if not json_output:
            console.print("[blue]Resolving references and building graph...[/blue]")
        self.code_graph.resolve_references()

        graph_saved = False
        graph_path_str = ""
        try:
            self.code_graph.save()
            graph_saved = True
            graph_path_str = str(self.code_graph.storage_path)
            if not json_output:
                console.print(
                    f"[green]✓ Dependency Graph saved to {graph_path_str} ({self.code_graph.graph.number_of_nodes()} nodes, {self.code_graph.graph.number_of_edges()} edges)[/green]"
                )
        except Exception as e:
            if not json_output:
                console.print(f"[red]Error saving graph: {e}[/red]")

        if not json_output:
            console.print(
                f"[green]✓ Analyzed and Indexed {len(self.results)} files successfully.[/green]"
            )

        summary = {
            "status": "success",
            "files_analyzed": len(self.results),
            "documents_indexed": len(documents),
            "graph_nodes": self.code_graph.graph.number_of_nodes(),
            "graph_edges": self.code_graph.graph.number_of_edges(),
            "graph_path": graph_path_str,
        }

        # Save summary to context.json
        try:
            import json

            with open(self.db_dir / "context.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
        except:
            pass

        return summary

    def _process_file(self, file_path, documents, metadatas, ids):
        try:
            result = self.parser.parse_file(file_path)
            if result:
                self.results.append(result)

                # Register file in graph
                self.code_graph.add_file(file_path.as_posix(), language=result["language"])

                # Register definitions
                for definition in result.get("definitions", []):
                    self.code_graph.add_definition(definition, file_path.as_posix())

                # Register calls (references)
                for call in result.get("calls", []):
                    self.code_graph.add_call(file_path.as_posix(), call)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 1. 파일 전체 인덱싱 (기존 호환성 유지)
                documents.append(content)
                metadatas.append(
                    {
                        "path": file_path.as_posix(),
                        "language": result["language"],
                        "type": "file",
                    }
                )
                ids.append(f"file:{file_path.as_posix()}")
                
                # 2. 함수/클래스 단위 Fine-grained 인덱싱 (Phase 3 추가)
                symbols = result.get("symbols", [])
                for symbol in symbols:
                    symbol_name = symbol.get("name", "")
                    symbol_code = symbol.get("code", "")
                    symbol_type = symbol.get("type", "function")
                    
                    if not symbol_name or not symbol_code:
                        continue
                    
                    # Docstring을 코드 앞에 추가 (검색 정확도 향상)
                    docstring = symbol.get("docstring", "")
                    searchable_content = symbol_code
                    if docstring:
                        searchable_content = f"# {docstring}\n{symbol_code}"
                    
                    symbol_id = f"symbol:{file_path.as_posix()}:{symbol_name}"
                    
                    documents.append(searchable_content)
                    metadatas.append({
                        "path": file_path.as_posix(),
                        "symbol": symbol_name,
                        "type": symbol_type,
                        "language": result["language"],
                        "start_line": symbol.get("start_line", 0),
                        "end_line": symbol.get("end_line", 0),
                    })
                    ids.append(symbol_id)

        except Exception as e:
            # Log warning instead of silent failure
            logger = get_logger()
            logger.warning(f"Failed to process file {file_path}: {e}")
            pass

    def analyze_incremental(self, json_output: bool = False) -> Dict[str, Any]:
        """
        증분 분석: 변경된 파일만 재인덱싱합니다.
        
        FileTracker를 사용하여 MD5 해시 기반으로 변경된 파일을 감지하고,
        해당 파일만 재파싱/재인덱싱하여 성능을 최적화합니다.
        
        Returns:
            Dict: 분석 결과 요약 (changed_files, unchanged_files 등)
        """
        if not self.project_path.exists():
            error_msg = f"Path {self.project_path} does not exist."
            if json_output:
                return {"status": "error", "message": error_msg}
            console.print(f"[bold red]Error:[/bold red] {error_msg}")
            return {"status": "error", "message": error_msg}
        
        # FileTracker 초기화
        tracker = FileTracker(self.db_dir)
        
        # 현재 파일 목록 스캔
        current_files = self.scan_files()
        
        # 변경 사항 감지
        changes = tracker.get_changes(current_files)
        
        if not changes.has_changes:
            if not json_output:
                console.print("[green]✓ No changes detected. Index is up-to-date.[/green]")
            return {
                "status": "success",
                "mode": "incremental",
                "changed_files": 0,
                "unchanged_files": len(changes.unchanged),
                "added_files": 0,
                "modified_files": 0,
                "deleted_files": 0,
            }
        
        # 변경된 파일 목록
        files_to_process = [Path(f) for f in changes.added + changes.modified]
        
        if not json_output:
            console.print(
                f"[bold blue][Incremental] Processing {len(files_to_process)} changed file(s)...[/bold blue]"
            )
            console.print(f"  • Added: {len(changes.added)}")
            console.print(f"  • Modified: {len(changes.modified)}")
            console.print(f"  • Deleted: {len(changes.deleted)}")
            console.print(f"  • Unchanged: {len(changes.unchanged)}")
        
        documents = []
        metadatas = []
        ids = []
        
        # 기존 그래프 로드
        try:
            self.code_graph.load()
        except:
            pass  # 첫 실행 시 그래프가 없을 수 있음
        
        # 삭제된 파일 처리: 그래프에서 노드 제거 및 벡터 스토어에서 삭제
        for deleted_file in changes.deleted:
            # 그래프에서 제거
            if deleted_file in self.code_graph.graph:
                self.code_graph.graph.remove_node(deleted_file)
            
            # 트래커에서 제거
            tracker.remove(deleted_file)
            
            # 벡터 스토어에서 삭제 (ID 패턴으로 삭제)
            try:
                file_id = f"file:{deleted_file}"
                self.vector_store.collection.delete(ids=[file_id])
            except:
                pass
        
        # 수정된 파일 처리: 기존 데이터 삭제 후 재인덱싱
        for modified_file in changes.modified:
            path_posix = Path(modified_file).as_posix()
            
            # 그래프에서 기존 노드 제거 (연관 엣지도 함께 제거됨)
            if path_posix in self.code_graph.graph:
                self.code_graph.graph.remove_node(path_posix)
            
            # 벡터 스토어에서 기존 문서 삭제
            try:
                file_id = f"file:{path_posix}"
                self.vector_store.collection.delete(ids=[file_id])
                
                # 심볼 문서도 삭제 (prefix 매칭)
                # ChromaDB는 where 조건으로 삭제 가능
                self.vector_store.collection.delete(
                    where={"path": path_posix}
                )
            except:
                pass
        
        # 변경/추가된 파일 처리
        if json_output:
            for file_path in files_to_process:
                self._process_file(file_path, documents, metadatas, ids)
        else:
            from rich.progress import Progress, SpinnerColumn, TextColumn
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Parsing & Indexing...", total=len(files_to_process))
                
                for file_path in files_to_process:
                    self._process_file(file_path, documents, metadatas, ids)
                    progress.advance(task)
        
        # 벡터 스토어에 새 문서 추가
        if documents:
            if not json_output:
                console.print(f"[blue]Embedding {len(documents)} documents...[/blue]")
            self.vector_store.add_documents(documents, metadatas, ids, quiet=json_output)
        
        # 그래프 참조 해석 및 저장
        if not json_output:
            console.print("[blue]Resolving references and building graph...[/blue]")
        self.code_graph.resolve_references()
        
        try:
            self.code_graph.save()
            if not json_output:
                console.print(
                    f"[green]✓ Graph updated ({self.code_graph.graph.number_of_nodes()} nodes, "
                    f"{self.code_graph.graph.number_of_edges()} edges)[/green]"
                )
        except Exception as e:
            if not json_output:
                console.print(f"[red]Error saving graph: {e}[/red]")
        
        # FileTracker 상태 업데이트 및 저장
        tracker.update_batch(files_to_process)
        for deleted_file in changes.deleted:
            tracker.remove(deleted_file)
        tracker.save()
        
        summary = {
            "status": "success",
            "mode": "incremental",
            "changed_files": changes.total_changed,
            "unchanged_files": len(changes.unchanged),
            "added_files": len(changes.added),
            "modified_files": len(changes.modified),
            "deleted_files": len(changes.deleted),
            "documents_indexed": len(documents),
            "graph_nodes": self.code_graph.graph.number_of_nodes(),
            "graph_edges": self.code_graph.graph.number_of_edges(),
        }
        
        if not json_output:
            console.print(
                f"[green]✓ Incremental update complete: "
                f"{changes.total_changed} changed, {len(changes.unchanged)} unchanged[/green]"
            )
        
        return summary

