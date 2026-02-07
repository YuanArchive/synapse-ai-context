import networkx as nx
from pathlib import Path
from typing import List, Dict, Set, Any, Optional
import json

class CodeGraph:
    """
    Manages the dependency graph of the codebase.
    """
    def __init__(self, storage_path: Optional[Path] = None):
        self.graph = nx.DiGraph()
        self.storage_path = storage_path
        
        # In-memory index for fast lookup of definitions
        # name -> list of file_paths
        self.definition_index: Dict[str, List[str]] = {}

    def add_file(self, file_path: str, language: str):
        """Add a file node to the graph."""
        self.graph.add_node(file_path, type="file", language=language)

    def add_definition(self, name: str, file_path: str):
        """
        Register a function/class definition.
        Adds a node for the definition and links it to the file.
        Also updates the definition index for resolution.
        """
        # Node for the symbol
        symbol_id = f"symbol:{name}"
        self.graph.add_node(symbol_id, type="symbol", name=name)
        
        # Edge: File -> Defines -> Symbol
        self.graph.add_edge(file_path, symbol_id, type="defines")
        
        # Update index
        if name not in self.definition_index:
            self.definition_index[name] = []
        if file_path not in self.definition_index[name]:
            self.definition_index[name].append(file_path)

    def add_call(self, caller_file: str, call_name: str):
        """
        Register a function call.
        Temporarily adds an edge from file to a 'call' placeholder or
        stores it for later resolution.
        """
        # We store the call as a node (or just an edge?)
        # For now, let's just record that file X calls name Y.
        # We will resolve 'name Y' to a symbol node later.
        
        # Store metadata on the file node or a temporary list?
        # Let's add a temporary "unresolved_call" edge to a placeholder
        # to preserve the information in the graph structure if needed,
        # OR just keep it in memory.
        
        # Better: Add edge File -> (calls) -> Symbol(name)
        # But we don't know which Symbol ID yet if there are multiple 'foo'.
        # So we'll use a placeholder ID for the name.
        
        # Actually, let's do it in `resolve_references`.
        # For now, we need to store "Caller File needs 'name'".
        # We can add an attribute to the file node.
        
        if not self.graph.has_node(caller_file):
            # Should have been added via add_file, but just in case
            self.graph.add_node(caller_file, type="file")
            
        # We append to a list of calls in the node data
        current_calls = self.graph.nodes[caller_file].get("calls", [])
        if call_name not in current_calls:
            current_calls.append(call_name)
            self.graph.nodes[caller_file]["calls"] = current_calls

    def resolve_references(self):
        """
        Link callers to definitions.
        For every file node, look at its 'calls'.
        Find matching definitions in `definition_index`.
        Add edges: CallerFile -> (calls) -> DefinedFile
        """
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "file":
                calls = data.get("calls", [])
                for call_name in calls:
                    # Find who defines this
                    defined_in_files = self.definition_index.get(call_name, [])
                    
                    for target_file in defined_in_files:
                        if target_file == node:
                            continue # Ignore self-calls for dependency graph (optional)
                            
                        # Add edge: Node -> Target
                        # We can add weight or count
                        self.graph.add_edge(node, target_file, type="calls", symbol=call_name)

    def get_related_files(self, file_path: str, depth: int = 1) -> List[str]:
        """
        Find related files (dependencies and dependents).
        Uses BFS to traverse the dependency graph up to specified depth.
        Returns files ordered by priority (direct deps first).
        
        Args:
            file_path: 시작 파일 경로
            depth: 탐색 깊이 (기본값: 1)
            
        Returns:
            List[str]: 관련 파일 경로 목록 (depth 기준 정렬)
        """
        from collections import deque
        
        if file_path not in self.graph:
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
                node_data = self.graph.nodes.get(current, {})
                if node_data.get("type") == "file":
                    result.append((current, current_depth))
            
            # 인접 노드 탐색 (successors = dependencies, predecessors = dependents)
            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    queue.append((neighbor, current_depth + 1))
            
            for neighbor in self.graph.predecessors(current):
                if neighbor not in visited:
                    queue.append((neighbor, current_depth + 1))
        
        # depth 기준 정렬 (가까운 파일 우선)
        result.sort(key=lambda x: x[1])
        return [f for f, d in result]


    def save(self):
        """Save graph to storage_path (GML)."""
        if self.storage_path:
            # Convert list attributes to strings for GML
            G_export = self.graph.copy()
            for n, d in G_export.nodes(data=True):
                for k, v in d.items():
                    if isinstance(v, list):
                        d[k] = ",".join(v)
            nx.write_gml(G_export, str(self.storage_path))

    def load(self):
        """Load graph from storage_path."""
        if self.storage_path and self.storage_path.exists():
            self.graph = nx.read_gml(str(self.storage_path))
            # Rebuild index? Or assume it's fresh?
            # Rebuilding index from graph structure:
            self.definition_index = {}
            for n, d in self.graph.nodes(data=True):
                if d.get("type") == "symbol":
                    name = d.get("name")
                    # Find files that define this symbol (predecessors with edge type 'defines')
                    # But in `resolve_references` I added File -> Symbol edge?
                    # Wait, in `add_definition`, I added File -> Symbol.
                    # So Predecessors of Symbol are Files.
                    if name:
                        preds = list(self.graph.predecessors(n))
                        self.definition_index[name] = preds

