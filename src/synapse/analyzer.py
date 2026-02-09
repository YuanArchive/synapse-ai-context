from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import concurrent.futures
import multiprocessing
import os

console = Console()

from .parser import CodeParser
from .vector_store import VectorStore
from .graph import CodeGraph
from .file_tracker import FileTracker, ChangeSet
from .exceptions import SynapseError, IndexingError, ParserError
from .logger import get_logger
import networkx as nx

# Global variable for worker processes to hold their own parser instance
_global_parser = None

def _get_worker_parser():
    """
    Lazy initialization of CodeParser in worker process.
    """
    global _global_parser
    if _global_parser is None:
        _global_parser = CodeParser()
    return _global_parser

def process_file_wrapper(file_path: Path) -> Tuple[Path, Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Worker function to process a single file.
    Returns: (file_path, parse_result, file_content, error_msg)
    """
    try:
        parser = _get_worker_parser()
        result = parser.parse_file(file_path)
        
        content = ""
        if result:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                return file_path, None, None, str(e)
                
        return file_path, result, content, None
    except Exception as e:
        return file_path, None, None, str(e)

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
        # Parser in main process is only for lightweight tasks if needed
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

    def _aggregate_results(self, file_path: Path, result: Dict, content: str, documents: List, metadatas: List, ids: List):
        """
        Aggregates results from worker execution into the main collections.
        """
        self.results.append(result)

        # Register file in graph
        self.code_graph.add_file(file_path.as_posix(), language=result["language"])

        # Register definitions
        for definition in result.get("definitions", []):
            self.code_graph.add_definition(definition, file_path.as_posix())

        # Register calls (references)
        for call in result.get("calls", []):
            self.code_graph.add_call(file_path.as_posix(), call)

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
        
        # 2. 함수/클래스 단위 Fine-grained 인덱싱
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

    def analyze(self, json_output: bool = False, num_workers: int = None):
        """
        Main analysis pipeline (Parallelized).
        """
        if not self.project_path.exists():
            error_msg = f"Path {self.project_path} does not exist."
            if json_output:
                return {"status": "error", "message": error_msg}
            console.print(f"[bold red]Error:[/bold red] {error_msg}")
            return

        files = self.scan_files()
        
        # workers count: default to CPU count, but at least 1
        max_workers = num_workers or os.cpu_count() or 1
        
        if not json_output:
            console.print(
                f"[bold blue]Analyzing {len(files)} files with {max_workers} workers...[/bold blue]"
            )

        documents = []
        metadatas = []
        ids = []

        # Initialize FileTracker for full analysis (to populate initial state)
        tracker = FileTracker(self.db_dir)
        tracker.update_batch(files) # We assume all valid if success
        tracker.save()

        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Prepare futures
            future_to_file = {executor.submit(process_file_wrapper, f): f for f in files}
            
            if json_output:
                for future in concurrent.futures.as_completed(future_to_file):
                    f_path, res, content, err = future.result()
                    if res and content:
                        self._aggregate_results(f_path, res, content, documents, metadatas, ids)
            else:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Parsing & Indexing...", total=len(files))
                    
                    for future in concurrent.futures.as_completed(future_to_file):
                        f_path, res, content, err = future.result()
                        if res and content:
                            self._aggregate_results(f_path, res, content, documents, metadatas, ids)
                        elif err:
                            # Log error but continue
                            logger = get_logger()
                            logger.warning(f"Failed to process {f_path}: {err}")
                        
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

    def analyze_incremental(self, json_output: bool = False, num_workers: int = None) -> Dict[str, Any]:
        """
        증분 분석: 변경된 파일만 재인덱싱합니다. (Parallelized)
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
            
            # 벡터 스토어에서 삭제
            try:
                file_id = f"file:{deleted_file}"
                self.vector_store.collection.delete(ids=[file_id])
                # 심볼 문서도 삭제 (ChromaDB where절 사용)
                self.vector_store.collection.delete(where={"path": deleted_file})
            except:
                pass
        
        # 수정된 파일 처리: 기존 데이터 삭제 후 재인덱싱
        for modified_file in changes.modified:
            path_posix = Path(modified_file).as_posix()
            
            # 그래프에서 기존 노드 제거
            if path_posix in self.code_graph.graph:
                self.code_graph.graph.remove_node(path_posix)
            
            # 벡터 스토어에서 기존 문서 삭제
            try:
                file_id = f"file:{path_posix}"
                self.vector_store.collection.delete(ids=[file_id])
                self.vector_store.collection.delete(where={"path": path_posix})
            except:
                pass
        
        # 변경/추가된 파일 병렬 처리
        max_workers = num_workers or os.cpu_count() or 1
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(process_file_wrapper, f): f for f in files_to_process}
            
            if json_output:
                for future in concurrent.futures.as_completed(future_to_file):
                    f_path, res, content, err = future.result()
                    if res and content:
                        self._aggregate_results(f_path, res, content, documents, metadatas, ids)
            else:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Parsing & Indexing...", total=len(files_to_process))
                    
                    for future in concurrent.futures.as_completed(future_to_file):
                        f_path, res, content, err = future.result()
                        if res and content:
                            self._aggregate_results(f_path, res, content, documents, metadatas, ids)
                        elif err:
                            logger = get_logger()
                            logger.warning(f"Failed to process {f_path}: {err}")
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

