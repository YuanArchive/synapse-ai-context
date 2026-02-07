import sys
from rich.console import Console

# Python 3.14+ Compatibility Check (due to ChromaDB/Pydantic v1)
if sys.version_info >= (3, 14):
    console = Console()
    console.print("[bold red]Error: Synapse is currently incompatible with Python 3.14+.[/bold red]")
    console.print("[yellow]ChromaDB (and Pydantic v1) has known issues with Python 3.14.[/yellow]")
    console.print("[bold cyan]Solution:[/bold cyan] Please use [bold]Python 3.12[/bold] (Recommended) or 3.13.")
    console.print("[dim]Suggested: python -m venv .venv (using Python 3.12)[/dim]\n")
    sys.exit(1)

import typer
import json
from typing import List, Optional, Union
from .analyzer import ProjectAnalyzer
from .vector_store import VectorStore
from .compressor import Compressor
from .graph import CodeGraph
from .prompts import DEEP_THINK_PROMPT
from .markdown_gen import MarkdownGenerator
from .context_manager import ContextManager, build_context
from .structure.pruner import ASTSkeletonizer, skeletonize_file
from .hybrid_search import HybridSearch, hybrid_search
from .exceptions import SynapseError
from .logger import get_logger
from pathlib import Path

app = typer.Typer(help="Synapse: AI Context Augmentation Tool")
console = Console()


def wrap_artifact(content: str, name: str) -> str:
    """
    Wrap content in <synapse-artifact> tags for AI agent consumption.
    """
    return f'<synapse-artifact name="{name}">\n{content}\n</synapse-artifact>'


def _print_protocol_reminder():
    """
    Print a random Synapse Protocol reminder to reinforce AI rules.
    """
    import random
    
    reminders = [
        "[bold cyan]Tip:[/bold cyan] 🔍 **Search Before You Strike** - 코드를 먼저 찾고 수정하세요. (No Guessing)",
        "[bold cyan]Tip:[/bold cyan] 🕸️ **Check the Graph** - `synapse graph`로 수정 영향도를 파악하세요.",
        "[bold cyan]Tip:[/bold cyan] 🧠 **Deep Think on Failure** - 에러 발생 시 `--think`로 심층 분석하세요.",
        "[bold cyan]Tip:[/bold cyan] 👁️ **Watch Mode** - `synapse watch start`로 실시간 인덱싱을 켜두세요.",
    ]
    

    console.print(f"\n{random.choice(reminders)}")


def _save_output(content: str, output_path: str):
    """
    Save content to a file and print a success message.
    """
    try:
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        console.print(f"[green]✓ Output saved to {path}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving output: {e}[/red]")


@app.command()
def init(
    path: str = typer.Option(".", help="Target project path"),
    agent: bool = typer.Option(
        True,
        "--agent",
        help="Initialize with generic Agent-optimized context structure (Default: True)",
    ),
    vscode: bool = typer.Option(
        False,
        "--vscode",
        help="Automatically generate .vscode/settings.json for the current environment",
    ),
):
    """
    Initialize Synapse in the target directory.
    Creates .synapse, .context, and .agent/ (with KO/EN rules).
    """
    import shutil
    import sys
    import json
    
    target = Path(path).resolve()
    synapse_dir = target / ".synapse"
    context_dir = target / ".context"
    agent_dir = target / ".agent"
    docs_dir = target / "docs"
    vscode_dir = target / ".vscode"

    console.print("## Synapse Initialization")

    # 1. Create .synapse
    if synapse_dir.exists():
        console.print("- [ ] `.synapse` directory already exists")
    else:
        synapse_dir.mkdir(parents=True, exist_ok=True)
        console.print("- [x] Created `.synapse` directory")

    # 2. Create .context
    if context_dir.exists():
        console.print("- [ ] `.context` directory already exists")
    else:
        context_dir.mkdir(parents=True, exist_ok=True)
        console.print("- [x] Created `.context` directory")

    # 3. Create .agent directory and copy rules
    if agent or not agent_dir.exists():
        exist_ok_flag = agent_dir.exists()
        agent_dir.mkdir(parents=True, exist_ok=True)
        if not exist_ok_flag:
            console.print("- [x] Created `.agent` directory")

        # Copy rule files from package templates
        try:
            import synapse
            template_dir = Path(synapse.__file__).parent / "templates"

            rules_to_copy = ["AI_RULES_KO.md", "AI_RULES_EN.md"]
            
            for rule_file in rules_to_copy:
                src = template_dir / rule_file
                dst = agent_dir / rule_file
                
                if src.exists():
                    if not dst.exists():
                        shutil.copy2(src, dst)
                        console.print(f"- [x] Installed `.agent/{rule_file}`")
                    else:
                        console.print(f"- [ ] `.agent/{rule_file}` already exists")
                else:
                    console.print(f"- [yellow]Warning: Source rule {rule_file} not found[/yellow]")
                    
        except Exception as e:
            console.print(f"- [red]Error copying rules: {e}[/red]")

    # 4. Create docs/ and copy manuals
    if not docs_dir.exists():
        docs_dir.mkdir(parents=True, exist_ok=True)
        console.print("- [x] Created `docs` directory")
    else:
        console.print("- [ ] `docs` directory already exists")
    
    # Copy documentation files from synapse package templates
    try:
        import synapse
        template_dir = Path(synapse.__file__).parent / "templates"
        
        if template_dir.exists():
            # MANUAL_KO.md 복사
            manual_src = template_dir / "MANUAL_KO.md"
            manual_dst = docs_dir / "SYNAPSE_MANUAL_KO.md"
            if manual_src.exists() and not manual_dst.exists():
                shutil.copy2(manual_src, manual_dst)
                console.print("- [x] Copied `docs/SYNAPSE_MANUAL_KO.md`")
            elif manual_dst.exists():
                console.print("- [ ] `docs/SYNAPSE_MANUAL_KO.md` already exists")
            
            # AGENT_BOOTSTRAP 복사 (KO/EN)
            bootstrap_files = ["AGENT_BOOTSTRAP_KO.md", "AGENT_BOOTSTRAP_EN.md"]
            
            for bs_file in bootstrap_files:
                src = template_dir / bs_file
                dst = docs_dir / bs_file
                
                if src.exists():
                    if not dst.exists():
                        shutil.copy2(src, dst)
                        console.print(f"- [x] Copied `docs/{bs_file}`")
                    else:
                        console.print(f"- [ ] `docs/{bs_file}` already exists")
                else:
                    console.print(f"- [yellow]Warning: Source {bs_file} not found[/yellow]")
        else:
            console.print("- [yellow]Warning: Source templates not found[/yellow]")
    except Exception as e:
        console.print(f"- [yellow]Warning: Could not copy docs: {e}[/yellow]")

    # 5. VS Code Configuration
    if vscode:
        try:
            vscode_dir.mkdir(parents=True, exist_ok=True)
            settings_path = vscode_dir / "settings.json"
            
            current_python = Path(sys.executable)
            
            # Check if python is inside the target project (portable venv)
            try:
                relative_python = current_python.relative_to(target)
                python_setting = f"./{relative_python.as_posix()}"
                console.print(f"- [x] Detected portable venv at `{python_setting}`")
            except ValueError:
                # Outside target project, use absolute path
                python_setting = current_python.as_posix()
                console.print(f"- [x] Detected external environment at `{python_setting}`")

            settings_data = {}
            if settings_path.exists():
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        settings_data = json.load(f)
                    except:
                        pass
            
            settings_data["python.defaultInterpreterPath"] = python_setting
            settings_data["python.terminal.activateEnvInCurrentTerminal"] = True
            
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings_data, f, indent=4)
            
            console.print("- [x] Generated `.vscode/settings.json`")
        except Exception as e:
            console.print(f"- [yellow]Warning: Could not setup VS Code: {e}[/yellow]")

    console.print("\n**Ready.** Run `python -m synapse analyze .` to start.")
    console.print("> Tip: AI 세팅은 `@docs/AGENT_BOOTSTRAP_KO.md`를 태그하세요.")


@app.command()
def analyze(
    path: str = typer.Argument(..., help="Target project path"),
    full: bool = typer.Option(
        False, "--full", help="Force full reindex (default: incremental update)"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output results in JSON format for machine consumption"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging for debugging"
    ),
):
    """
    지정된 경로의 프로젝트를 분석하여 RAG 인덱스를 생성하고 의존성 그래프를 그립니다.
    
    기본 동작: 변경된 파일만 증분 업데이트 (빠름)
    --full 옵션: 전체 재인덱싱 강제 실행
    --verbose 옵션: 상세 로그 출력
    """
    # 로거 초기화
    log_dir = Path(path).resolve() / ".synapse"
    logger = get_logger(verbose=verbose, log_dir=log_dir if not json_output else None)
    logger.debug(f"Starting analysis: path={path}, full={full}")
    
    try:
        analyzer = ProjectAnalyzer(path)

        if json_output:
            if full:
                summary = analyzer.analyze(json_output=True)
            else:
                summary = analyzer.analyze_incremental(json_output=True)
            # Always generate INTELLIGENCE.md, but quietly
            _summarize_internal(path, output_dir=str(Path(path) / ".synapse"), quiet=True)
            console.print(json.dumps(summary, indent=2))
            return

        # Markdown Output
        if full:
            console.print(f"## Synapse Analysis (Full): `{path}`")
            console.print("Starting full reindex...")
            summary = analyzer.analyze(json_output=True) or {}
        else:
            console.print(f"## Synapse Analysis (Incremental): `{path}`")
            console.print("Checking for changes...")
            summary = analyzer.analyze_incremental(json_output=True) or {}

        if summary.get("status") == "error":
            console.print(f"\n### Error\n{summary.get('message')}")
            return

        console.print("\n### Summary")
        console.print(f"- **Status:** {summary.get('status')}")
        console.print(f"- **Mode:** {summary.get('mode', 'full')}")
        
        if summary.get('mode') == 'incremental':
            console.print(f"- **Changed Files:** {summary.get('changed_files', 0)}")
            console.print(f"  - Added: {summary.get('added_files', 0)}")
            console.print(f"  - Modified: {summary.get('modified_files', 0)}")
            console.print(f"  - Deleted: {summary.get('deleted_files', 0)}")
            console.print(f"- **Unchanged Files:** {summary.get('unchanged_files', 0)}")
        else:
            console.print(f"- **Files Analyzed:** {summary.get('files_analyzed')}")
        
        console.print(f"- **Documents Indexed:** {summary.get('documents_indexed')}")
        console.print(f"- **Graph Nodes:** {summary.get('graph_nodes')}")
        console.print(f"- **Graph Edges:** {summary.get('graph_edges')}")
        if summary.get('graph_path'):
            console.print(f"- **Graph Path:** `{summary.get('graph_path')}`")

        # Auto-generate INTELLIGENCE.md in .synapse/
        _summarize_internal(path, output_dir=str(Path(path) / ".synapse"), quiet=False)

        console.print("\n> Analysis complete. Ready for `python -m synapse search`.")
        logger.info(f"Analysis complete: {summary.get('files_analyzed', summary.get('changed_files', 0))} files processed")
        
        _print_protocol_reminder()
        
    except SynapseError as e:
        logger.error(f"Synapse error: {e.message}")
        if json_output:
            console.print(json.dumps(e.to_dict()))
        else:
            console.print(f"[red]Error: {e.message}[/red]")
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        if json_output:
            console.print(json.dumps({"error": "unexpected", "message": str(e)}))
        else:
            console.print(f"[red]Unexpected error: {e}[/red]")


@app.command()
def summarize(
    path: str = typer.Argument(".", help="Target project path"),
    output_dir: Optional[str] = typer.Option(
        None, help="Directory to save the markdown file"
    ),
):
    """
    Generate an INTELLIGENCE.md file summarizing the project for AI agents.
    """
    _summarize_internal(path, output_dir, quiet=False)


def _summarize_internal(
    path: str, output_dir: Optional[str] = None, quiet: bool = False
):
    target_path = Path(path).resolve()
    synapse_dir = target_path / ".synapse"

    if not synapse_dir.exists():
        if not quiet:
            console.print(
                f"[red]Error: .synapse directory not found. Run 'python -m synapse analyze .' first.[/red]"
            )
        return

    # Load Graph
    graph_path = synapse_dir / "dependency_graph.gml"
    code_graph = CodeGraph(storage_path=graph_path)
    try:
        code_graph.load()
    except Exception as e:
        if not quiet:
            console.print(f"[red]Error loading graph: {e}[/red]")
        return

    summary_path = synapse_dir / "context.json"
    summary = {}
    if summary_path.exists():
        with open(summary_path, "r") as f:
            summary = json.load(f)
    else:
        summary = {
            "files_analyzed": len(
                [
                    n
                    for n, d in code_graph.graph.nodes(data=True)
                    if d.get("type") == "file"
                ]
            ),
            "graph_nodes": code_graph.graph.number_of_nodes(),
            "graph_edges": code_graph.graph.number_of_edges(),
        }

    gen = MarkdownGenerator(target_path, summary, code_graph.graph)
    markdown = gen.generate()

    out_dir = Path(output_dir) if output_dir else synapse_dir
    out_dir.mkdir(exist_ok=True, parents=True)
    output_file = out_dir / "INTELLIGENCE.md"

    output_file.write_text(markdown, encoding="utf-8")

    if not quiet:
        console.print(f"[green]✓ Generated {output_file}[/green]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    path: str = typer.Option(".", help="Project root path (containing .synapse)"),
    limit: int = typer.Option(5, help="Maximum number of results"),
    hybrid: bool = typer.Option(
        False, "--hybrid", help="Use Graph RAG (Vector + Graph) for better accuracy"
    ),
    compress: bool = typer.Option(
        False, "--compress", help="Compress output using LLMLingua"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output results in JSON format for machine consumption"
    ),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save output to a file"),
):
    """
    인덱싱된 코드베이스에서 시맨틱 검색을 수행합니다.
    
    --hybrid 옵션을 사용하면 Vector Search + Graph Traversal을 결합하여
    더 정확한 컨텍스트를 찾습니다. (Graph RAG)
    """
    synapse_dir = Path(path).resolve() / ".synapse"
    if not synapse_dir.exists():
        msg = f".synapse directory not found in {path}. Run 'analyze' first."
        if json_output:
            console.print(json.dumps({"error": msg}))
        else:
            console.print(f"## Error\n{msg}")
        return

    # Auto-Index: Check for changes and update if needed
    try:
        analyzer = ProjectAnalyzer(path)
        summary = analyzer.analyze_incremental(json_output=True)
        
        if summary.get("status") == "success" and summary.get("changed_files", 0) > 0:
            if not json_output:
                n = summary.get("changed_files")
                console.print(f"[dim]⚡ Index synced: {n} files updated[/dim]")
    except Exception:
        # Fail silently on auto-index to not block search
        pass


    db_path = str(synapse_dir / "db")
    vs = VectorStore(db_path=db_path)
    
    # Hybrid Search 모드
    if hybrid:
        graph_path = synapse_dir / "dependency_graph.gml"
        code_graph = CodeGraph(storage_path=graph_path)
        try:
            code_graph.load()
        except Exception:
            if not json_output:
                console.print("[yellow]Warning: Graph not loaded, falling back to vector search[/yellow]")
            hybrid = False
    
    if hybrid:
        searcher = HybridSearch(vs, code_graph)
        hybrid_results = searcher.search(query, top_k=limit)
        
        if not hybrid_results.results:
            if json_output:
                console.print(json.dumps([]))
            else:
                console.print(f"## Hybrid Search Results for `{query}`\n\nNo relevant code found.")
            return
        
        # Hybrid 결과 처리
        output_data = []
        for r in hybrid_results.results:
            output_data.append({
                "score": float(r.hybrid_score),
                "vector_score": float(r.vector_score),
                "graph_score": float(r.graph_score),
                "path": r.node_id,
                "relation": r.relation_type,
                "depth": r.depth_from_seed,
                "snippet": r.content[:500] if len(r.content) > 500 else r.content,
            })
        
        if json_output:
            console.print(json.dumps(output_data, indent=2))
            return
        
        # Markdown 출력
        search_md = f"## Hybrid Search Results for `{query}`\n\n"
        search_md += f"**Seeds:** {hybrid_results.seeds_count} | **Expanded:** {hybrid_results.expanded_count}\n\n"
        
        for i, r in enumerate(hybrid_results.results, 1):
            search_md += f"### {i}. `{r.node_id}`\n"
            search_md += f"- **Hybrid Score:** {r.hybrid_score:.3f} (Vector: {r.vector_score:.3f}, Graph: {r.graph_score:.3f})\n"
            search_md += f"- **Relation:** {r.relation_type} (depth: {r.depth_from_seed})\n"
            snippet = r.content[:300] if len(r.content) > 300 else r.content
            search_md += f"\n```python\n{snippet}\n```\n\n"
        
        console.print(wrap_artifact(search_md, "hybrid_search_results"))
        if output:
            _save_output(search_md, output)
        return
    
    # 기존 Vector Search
    results = vs.query(query, n_results=limit)

    if not results or not results.get("documents"):
        if json_output:
            console.print(json.dumps([]))
        else:
            console.print(f"## Search Results for `{query}`\n\nNo relevant code found.")
        return

    # ChromaDB returns nested lists
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results.get("distances", [[0] * limit])[0]

    output_data = []

    compressor = None
    if compress:
        try:
            if not json_output:
                console.print(
                    "[dim]Initializing compression engine (distilgpt2)...[/dim]"
                )
            compressor = Compressor()
        except Exception as e:
            if not json_output:
                console.print(
                    f"[bold red]Warning:[/bold red] Failed to load compressor: {e}"
                )
            compress = False

    for doc, meta, dist in zip(documents, metadatas, distances):
        snippet = doc
        if compress and compressor:
            # Using 20% retention rate (5x compression) for code to be safe yet effective
            snippet = compressor.compress(snippet, rate=0.2, question=query)

        output_data.append(
            {
                "score": float(dist),
                "path": meta.get("path", "unknown"),
                "snippet": snippet,
                "language": meta.get("language", ""),
            }
        )

    if json_output:
        console.print(json.dumps(output_data, indent=2))
        return

    # Load Graph for Extended Context
    graph_path = synapse_dir / "dependency_graph.gml"
    code_graph = CodeGraph(storage_path=graph_path)
    try:
        code_graph.load()
    except:
        # If graph fails to load, proceed without it
        pass

    results_md = f"## Search Results for `{query}`\n"

    for i, item in enumerate(output_data, 1):
        snippet = item["snippet"].strip()
        path_str = item["path"]
        lang = item["language"].lstrip(".")

        results_md += f"\n### {i}. {path_str} (Score: {item['score']:.4f})\n"
        results_md += f"```{lang}\n"
        results_md += snippet + "\n"
        results_md += "```\n"

        # Graph RAG: Show related files
        related = code_graph.get_related_files(path_str)
        if related:
            results_md += f"\n**🔗 Related Files (Graph RAG):**\n"
            for rel in related:
                if not rel.startswith("symbol:"):
                    results_md += f"- `{rel}`\n"

    if len(results_md) > 500:
        if output:
            _save_output(results_md, output)
        else:
            console.print(wrap_artifact(results_md, "search_results"))
    else:
        if output:
            _save_output(results_md, output)
        else:
            console.print(results_md)

    _print_protocol_reminder()


@app.command()
def ask(
    query: str = typer.Argument(..., help="User question"),
    path: str = typer.Option(".", help="Project root path (containing .synapse)"),
    limit: int = typer.Option(5, help="Maximum number of context results"),
    think: bool = typer.Option(
        False, "--think", help="Enable Deep Think Mode (Chain of Thought)"
    ),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save output to a file"),
):
    """
    Generate a prompt with retrieved context for the LLM.
    """
    synapse_dir = Path(path).resolve() / ".synapse"
    if not synapse_dir.exists():
        console.print(
            f"[red]Error: .synapse directory not found in {path}. Run 'python -m synapse analyze .' first.[/red]"
        )
        return

    # 1. Search Vector DB
    db_path = str(synapse_dir / "db")
    vs = VectorStore(db_path=db_path)
    results = vs.query(query, n_results=limit)

    context_files = set()
    context_snippets = []

    if results and results.get("documents"):
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        for doc, meta in zip(documents, metadatas):
            file_path = meta.get("path")
            if file_path:
                context_files.add(file_path)
                context_snippets.append(f"File: {file_path}\nCode:\n{doc}")

    # 2. Graph Expansion
    graph_path = synapse_dir / "dependency_graph.gml"
    code_graph = CodeGraph(storage_path=graph_path)
    try:
        code_graph.load()
        expanded_files = set()
        for f in context_files:
            related = code_graph.get_related_files(f)
            for r in related:
                # Filter out symbols and existing files
                if r not in context_files and not r.startswith("symbol:"):
                    expanded_files.add(r)

        if expanded_files:
            context_snippets.append("\n# Linked Files (Graph Context)")
            for ef in expanded_files:
                # We should ideally fetch content of these files, but for now just listing them
                # Or read them if possible. Let's read them for better context.
                try:
                    with open(ef, "r", encoding="utf-8") as f:
                        content = f.read()
                        context_snippets.append(
                            f"File: {ef} (Linked)\nCode:\n{content}"
                        )
                except:
                    context_snippets.append(
                        f"File: {ef} (Linked) - [Content Read Error]"
                    )
    except Exception as e:
        # Graph load failure is non-critical
        pass

    # 3. Construct Prompt
    final_prompt = ""

    if think:
        final_prompt += DEEP_THINK_PROMPT + "\n\n"

    final_prompt += f"Question: {query}\n\n"

    context_str = "\n---\n".join(context_snippets)
    final_prompt += "### Context:\n"
    final_prompt += wrap_artifact(context_str, "retrieved_context")

    final_prompt += wrap_artifact(context_str, "retrieved_context")

    if output:
        _save_output(final_prompt, output)
    else:
        console.print(final_prompt)
    
    _print_protocol_reminder()


@app.command()
def graph(
    file_path: str = typer.Argument(..., help="Target file path to analyze"),
    path: str = typer.Option(".", help="Project root path (containing .synapse)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save output to a file"),
):
    """
    Visualize dependencies (Imports/Calls) and dependents (Callers) for a file.
    """
    synapse_dir = Path(path).resolve() / ".synapse"
    if not synapse_dir.exists():
        console.print(
            "[red]Error: .synapse directory not found. Run 'python -m synapse analyze .' first.[/red]"
        )
        return

    graph_path = synapse_dir / "dependency_graph.gml"
    code_graph = CodeGraph(storage_path=graph_path)
    try:
        code_graph.load()
    except Exception as e:
        console.print(f"[red]Error loading graph: {e}[/red]")
        return

    target = Path(file_path).resolve().as_posix()

    # Try to find the node. If exact match fails, try relative path matching
    if target not in code_graph.graph:
        # Fallback: try to find by suffix
        # This is a bit risky but useful for relative paths
        candidates = [
            n
            for n in code_graph.graph.nodes
            if str(n).endswith(file_path)
            and code_graph.graph.nodes[n].get("type") == "file"
        ]
        if len(candidates) == 1:
            target = candidates[0]
        elif len(candidates) > 1:
            console.print(
                f"[yellow]Ambiguous path. Did you mean one of these?[/yellow]"
            )
            for c in candidates:
                console.print(f"- {c}")
            return
        else:
            console.print(f"[red]File node not found in graph: {target}[/red]")
            return

    graph_md = f"## Dependency Graph for `{target}`\n"

    # Dependencies (Outgoing edges: File -> File (calls))
    successors = list(code_graph.graph.successors(target))
    dependencies = []
    defines = []

    for succ in successors:
        edge_data = code_graph.graph.get_edge_data(target, succ)
        succ_data = code_graph.graph.nodes[succ]

        if edge_data.get("type") == "calls":
            dependencies.append((succ, edge_data.get("symbol", "?")))
        elif edge_data.get("type") == "defines":
            defines.append(succ_data.get("name", succ))

    # Dependents (Incoming edges: File (calls) -> This File)
    predecessors = list(code_graph.graph.predecessors(target))
    dependents = []

    for pred in predecessors:
        edge_data = code_graph.graph.get_edge_data(pred, target)
        if edge_data.get("type") == "calls":
            dependents.append((pred, edge_data.get("symbol", "?")))

    graph_md += "\n### 📤 Dependencies (Calls)\n"
    if dependencies:
        for dep_file, symbol in dependencies:
            graph_md += f"- Calls `{symbol}` in `{dep_file}`\n"
    else:
        graph_md += "[dim]No external dependencies found.[/dim]\n"

    graph_md += "\n### 📥 Dependents (Called By)\n"
    if dependents:
        for dep_file, symbol in dependents:
            graph_md += f"- Called by `{dep_file}` (via `{symbol}`)\n"
    else:
        graph_md += "[dim]No dependents found.[/dim]\n"

    graph_md += "\n### 📝 Defines\n"
    if defines:
        for name in defines:
            graph_md += f"- `{name}`\n"

    if output:
        _save_output(graph_md, output)
    else:
        console.print(wrap_artifact(graph_md, "dependency_graph"))
    
    _print_protocol_reminder()


@app.command()
def context(
    file_path: str = typer.Argument(..., help="Active file to build context for"),
    path: str = typer.Option(".", help="Project root path (containing .synapse)"),
    depth: int = typer.Option(2, help="Dependency traversal depth"),
    max_files: int = typer.Option(20, help="Maximum reference files to include"),
    json_output: bool = typer.Option(
        False, "--json", help="Output results in JSON format"
    ),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save output to a file"),
):
    """
    Active 파일 기준으로 최적화된 계층적 컨텍스트를 생성합니다.
    
    ⚡ 토큰 절약 (정보 손실 없음):
    - Reference 파일들은 Skeleton으로 압축 (구조만 유지)
    - Active 파일은 Full Code 유지 (절대 자르지 않음)
    
    3-Level 구조:
    - Level 0 (Global): 프로젝트 트리 + INTELLIGENCE.md
    - Level 1 (Reference): Import된 파일들의 Skeleton
    - Level 2 (Active): 현재 작업 파일 Full Code
    """
    synapse_dir = Path(path).resolve() / ".synapse"
    if not synapse_dir.exists():
        msg = f".synapse directory not found in {path}. Run 'analyze' first."
        if json_output:
            console.print(json.dumps({"error": msg}))
        else:
            console.print(f"## Error\n{msg}")
        return
    
    try:
        manager = ContextManager(
            project_path=Path(path),
            depth=depth,
            max_reference_files=max_files
        )
        result = manager.build_context(Path(file_path))
        
        if json_output:
            output = {
                "total_tokens": result.total_tokens,
                "token_breakdown": result.token_breakdown,
                "included_files": result.included_files,
                "savings": {
                    "original_tokens": result.savings.original_tokens if result.savings else 0,
                    "optimized_tokens": result.savings.optimized_tokens if result.savings else 0,
                    "saved_tokens": result.savings.saved_tokens if result.savings else 0,
                    "savings_ratio": result.savings.savings_ratio if result.savings else 0,
                },
                "global_context": result.global_context,
                "reference_context": result.reference_context,
                "active_context": result.active_context,
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Markdown 출력
            console.print(f"## Hierarchical Context for `{file_path}`\n")
            
            # 토큰 절약 효과 표시
            if result.savings:
                savings_pct = result.savings.savings_ratio * 100
                console.print(f"**📊 Token Efficiency:**")
                console.print(f"- Original: {result.savings.original_tokens:,} tokens")
                console.print(f"- Optimized: {result.savings.optimized_tokens:,} tokens")
                console.print(f"- **Saved: {result.savings.saved_tokens:,} tokens ({savings_pct:.1f}%)**")
            
            console.print(f"\n**Breakdown:** Global={result.token_breakdown.get('global', 0)}, "
                         f"Reference={result.token_breakdown.get('reference', 0)}, "
                         f"Active={result.token_breakdown.get('active', 0)}")
            
            if result.included_files:
                console.print(f"\n**Reference Files ({len(result.included_files)}):**")
                for f in result.included_files:
                    console.print(f"- `{f}`")
            
            console.print("\n---\n")
            if output:
                _save_output(result.formatted_output, output)
            else:
                console.print(wrap_artifact(result.formatted_output, "hierarchical_context"))
            
            _print_protocol_reminder()
    
    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error building context: {e}[/red]")


@app.command()
def skeleton(
    file_path: str = typer.Argument(..., help="File to skeletonize"),
    json_output: bool = typer.Option(
        False, "--json", help="Output results in JSON format"
    ),
):
    """
    파일을 Skeleton으로 변환합니다. (함수/클래스 시그니처만 유지)
    
    AST 기반으로 코드의 구조만 추출하여 토큰을 절약합니다.
    - 함수/클래스 시그니처 + Docstring 유지
    - 함수 Body는 ... 로 대체
    - Import 문 유지
    """
    target = Path(file_path)
    if not target.exists():
        msg = f"File not found: {file_path}"
        if json_output:
            console.print(json.dumps({"error": msg}))
        else:
            console.print(f"[red]Error: {msg}[/red]")
        return
    
    try:
        skeletonizer = ASTSkeletonizer()
        result = skeletonizer.skeletonize_file(target)
        
        if json_output:
            output = {
                "original_lines": result.original_lines,
                "skeleton_lines": result.skeleton_lines,
                "reduction_ratio": result.reduction_ratio,
                "skeleton": result.skeleton,
            }
            console.print(json.dumps(output, indent=2))
        else:
            console.print(f"## Skeleton: `{file_path}`\n")
            console.print(f"**Original:** {result.original_lines} lines | "
                         f"**Skeleton:** {result.skeleton_lines} lines | "
                         f"**Reduction:** {result.reduction_ratio:.1%}")
            console.print("\n```python")
            console.print(result.skeleton)
            console.print("```")
    
    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error: {e}[/red]")


# ============================================================
# Watch Commands - File Watcher Daemon
# ============================================================

watch_app = typer.Typer(help="File Watcher commands for real-time indexing")
app.add_typer(watch_app, name="watch")


@watch_app.command("start")
def watch_start(
    path: str = typer.Option(".", help="Project root path to watch"),
    debounce: float = typer.Option(2.0, help="Debounce delay in seconds"),
    daemon: bool = typer.Option(
        False, "--daemon", "-d", help="Run in background (detached process)"
    ),
):
    """
    파일 변경 감시를 시작합니다.
    
    파일이 변경되면 자동으로 증분 인덱싱을 수행합니다.
    --daemon 옵션 없이 실행하면 포그라운드에서 실행됩니다 (Ctrl+C로 종료).
    """
    try:
        from .watcher import SynapseWatcher, is_watchdog_available
    except ImportError:
        console.print("[red]Error: watchdog 패키지가 설치되지 않았습니다.[/red]")
        console.print("설치: pip install watchdog")
        return
    
    if not is_watchdog_available():
        console.print("[red]Error: watchdog 패키지가 설치되지 않았습니다.[/red]")
        console.print("설치: pip install watchdog")
        return
    
    project_path = Path(path).resolve()
    synapse_dir = project_path / ".synapse"
    
    if not synapse_dir.exists():
        console.print("[yellow]Warning: .synapse 디렉토리가 없습니다. 먼저 'synapse analyze'를 실행하세요.[/yellow]")
    
    # 이미 실행 중인지 확인
    status = SynapseWatcher.get_status(project_path)
    if status.running:
        console.print(f"[yellow]Watcher가 이미 실행 중입니다 (PID: {status.pid})[/yellow]")
        return
    
    if daemon:
        # 백그라운드 프로세스로 실행
        import subprocess
        import sys
        
        cmd = [
            sys.executable, "-m", "synapse.cli",
            "watch", "start", "--path", str(project_path),
            "--debounce", str(debounce)
        ]
        
        # Windows에서 백그라운드 실행
        if sys.platform == "win32":
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.Popen(
                cmd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        console.print(f"[green]✓ Watcher started in background for: {project_path}[/green]")
        console.print("상태 확인: synapse watch status")
        console.print("중지: synapse watch stop")
        return
    
    # 포그라운드 실행
    console.print(f"## Synapse Watcher")
    console.print(f"Watching: `{project_path}`")
    console.print(f"Debounce: {debounce}s")
    console.print("Press Ctrl+C to stop.\n")
    
    watcher = SynapseWatcher(
        project_path=project_path,
        debounce_seconds=debounce,
        quiet=False
    )
    watcher.run_forever()


@watch_app.command("status")
def watch_status(
    path: str = typer.Option(".", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """
    Watcher 상태를 확인합니다.
    """
    try:
        from .watcher import SynapseWatcher, is_watchdog_available
    except ImportError:
        if json_output:
            console.print(json.dumps({"error": "watchdog not installed", "running": False}))
        else:
            console.print("[red]watchdog 패키지가 설치되지 않았습니다.[/red]")
        return
    
    project_path = Path(path).resolve()
    status = SynapseWatcher.get_status(project_path)
    
    if json_output:
        console.print(json.dumps(status.to_dict(), indent=2))
        return
    
    console.print("## Synapse Watcher Status\n")
    
    if status.running:
        console.print(f"- **Status:** 🟢 Running")
        console.print(f"- **PID:** {status.pid}")
        console.print(f"- **Project:** `{status.project_path}`")
        console.print(f"- **Started:** {status.started_at}")
        console.print(f"- **Events Processed:** {status.events_processed}")
        if status.last_update:
            console.print(f"- **Last Update:** {status.last_update}")
    else:
        console.print(f"- **Status:** ⚫ Stopped")
        console.print(f"- **Project:** `{project_path}`")
        console.print("\n> 시작하려면: `synapse watch start`")


@watch_app.command("stop")
def watch_stop(
    path: str = typer.Option(".", help="Project root path"),
):
    """
    Watcher를 중지합니다.
    """
    try:
        from .watcher import SynapseWatcher
    except ImportError:
        console.print("[red]watchdog 패키지가 설치되지 않았습니다.[/red]")
        return
    
    project_path = Path(path).resolve()
    status = SynapseWatcher.get_status(project_path)
    
    if not status.running:
        console.print("[yellow]Watcher가 실행 중이 아닙니다.[/yellow]")
        return
    
    # 프로세스 종료
    import os
    import signal
    
    try:
        if status.pid:
            if os.name == 'nt':  # Windows
                os.kill(status.pid, signal.SIGTERM)
            else:
                os.kill(status.pid, signal.SIGTERM)
            
            console.print(f"[green]✓ Watcher stopped (PID: {status.pid})[/green]")
            
            # 상태 파일 제거
            status_file = project_path / ".synapse" / "watcher_status.json"
            if status_file.exists():
                status_file.unlink()
    except (ProcessLookupError, PermissionError) as e:
        console.print(f"[red]Error stopping watcher: {e}[/red]")
        # 상태 파일은 정리
        status_file = project_path / ".synapse" / "watcher_status.json"
        if status_file.exists():
            status_file.unlink()


if __name__ == "__main__":
    app()

