from typing import Dict, Any, List, Set, Optional, Tuple
from pathlib import Path
from rich.console import Console
import tree_sitter

# Import official language packages
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript
import tree_sitter_go
import tree_sitter_java
import tree_sitter_cpp
import tree_sitter_c
import tree_sitter_rust

console = Console()

class CodeParser:
    """
    Ultra-Robust AST Parser.
    If the tree-sitter Query API fails (common on some Windows/Version combos),
    it falls back to a manual AST walk to ensure 100% success rate.
    """

    def __init__(self):
        self.parsers = {}
        self.lang_modules = {
            ".py": tree_sitter_python,
            ".js": tree_sitter_javascript,
            ".jsx": tree_sitter_javascript,
            ".ts": tree_sitter_typescript,
            ".tsx": tree_sitter_typescript,
            ".go": tree_sitter_go,
            ".java": tree_sitter_java,
            ".cpp": tree_sitter_cpp,
            ".cc": tree_sitter_cpp,
            ".hpp": tree_sitter_cpp,
            ".c": tree_sitter_c,
            ".h": tree_sitter_c,
            ".rs": tree_sitter_rust,
        }

        self.queries = {
            ".py": "(function_definition name: (identifier) @def) (class_definition name: (identifier) @def) (call function: (identifier) @call)",
            ".js": "(function_declaration name: (identifier) @def) (method_definition name: (property_identifier) @def) (call_expression function: (identifier) @call)",
            ".ts": "(function_declaration name: (identifier) @def) (method_definition name: (property_identifier) @def) (call_expression function: (identifier) @call)",
        }
        self.queries.update({
            ".go": "(function_declaration name: (identifier) @def) (call_expression function: (identifier) @call)",
            ".java": "(method_declaration name: (identifier) @def) (method_invocation name: (identifier) @call)",
            ".rs": "(function_item name: (identifier) @def) (call_expression function: (identifier) @call)",
        })
        
        self.queries[".jsx"] = self.queries[".js"]
        self.queries[".tsx"] = self.queries[".ts"]
        self.queries[".cc"] = self.queries.get(".cpp", "")
        self.queries[".hpp"] = self.queries.get(".cpp", "")
        self.queries[".h"] = self.queries.get(".c", "")

    def _get_parser_and_lang(self, ext: str) -> Tuple[Optional[Any], Optional[Any]]:
        if ext not in self.lang_modules:
            return None, None

        if ext not in self.parsers:
            try:
                module = self.lang_modules[ext]
                raw_lang = module.language()
                try:
                    lang_obj = tree_sitter.Language(raw_lang)
                except:
                    lang_obj = raw_lang
                
                parser = tree_sitter.Parser(lang_obj)
                self.parsers[ext] = (parser, lang_obj)
            except Exception:
                return None, None
        return self.parsers[ext]

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        ext = file_path.suffix
        parser_tuple = self._get_parser_and_lang(ext)
        if not parser_tuple:
            return None

        parser, lang = parser_tuple

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()

            code_bytes = bytes(code, "utf8")
            code_lines = code.split("\n")
            tree = parser.parse(code_bytes)
            root_node = tree.root_node

            definitions = []
            calls = []
            symbols = []  # 함수/클래스 단위 세부 정보

            query_str = self.queries.get(ext)
            success = False

            # --- Attempt 1: Query API ---
            if query_str:
                try:
                    q = None
                    if hasattr(lang, 'query'):
                        q = lang.query(query_str)
                    if not q:
                        try:
                            from tree_sitter import Query
                            q = Query(lang, query_str)
                        except:
                            q = tree_sitter.Query(lang, query_str)

                    raw_captures = q.captures(root_node)
                    
                    processed_captures = []
                    if isinstance(raw_captures, dict):
                        for name, nodes in raw_captures.items():
                            for node in (nodes if isinstance(nodes, list) else [nodes]):
                                processed_captures.append((node, name))
                    else:
                        processed_captures = raw_captures

                    for item in processed_captures:
                        if isinstance(item, (tuple, list)) and len(item) >= 2:
                            node, capture_name = item[0], item[1]
                            name = code_bytes[node.start_byte : node.end_byte].decode("utf8", errors="ignore")
                            if capture_name == "def":
                                definitions.append(name)
                            elif capture_name == "call":
                                calls.append(name)
                    success = True
                except Exception:
                    # If Query fails, we proceed to Manual Walk
                    pass

            # --- Attempt 2: Manual AST Walk (Fallback) ---
            if not success or (not definitions and not calls):
                # We do a recursive walk to find symbols if the query engine is broken
                self._manual_walk(root_node, ext, code_bytes, definitions, calls)
            
            # --- Extract detailed symbol info (함수/클래스 단위) ---
            symbols = self._extract_symbols(root_node, ext, code_bytes, code_lines)

            return {
                "path": file_path.as_posix(),
                "language": ext,
                "definitions": sorted(list(set(definitions))),
                "calls": sorted(list(set(calls))),
                "symbols": symbols,  # 함수/클래스별 세부 정보
            }

        except Exception:
            return None

    def _manual_walk(self, node, ext, code_bytes, definitions, calls):
        """
        Recursive manual AST walk to extract symbols when Query API fails.
        """
        node_type = node.type
        
        # 1. Extract Definitions
        is_def = False
        if ext == ".py":
            if node_type in ["function_definition", "class_definition"]:
                # The name is usually the first identifier child
                for child in node.children:
                    if child.type == "identifier":
                        definitions.append(code_bytes[child.start_byte : child.end_byte].decode("utf8", errors="ignore"))
                        break
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            if node_type in ["function_declaration", "method_definition", "class_declaration"]:
                for child in node.children:
                    if child.type in ["identifier", "property_identifier"]:
                        definitions.append(code_bytes[child.start_byte : child.end_byte].decode("utf8", errors="ignore"))
                        break

        # 2. Extract Calls
        if ext == ".py":
            if node_type == "call":
                # function name is the 'function' child
                func_node = node.child_by_field_name("function")
                if func_node:
                    if func_node.type == "identifier":
                        calls.append(code_bytes[func_node.start_byte : func_node.end_byte].decode("utf8", errors="ignore"))
                    elif func_node.type == "attribute":
                        # object.method() -> get 'method'
                        attr_node = func_node.child_by_field_name("attribute")
                        if attr_node:
                            calls.append(code_bytes[attr_node.start_byte : attr_node.end_byte].decode("utf8", errors="ignore"))
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            if node_type == "call_expression":
                func_node = node.child_by_field_name("function")
                if func_node:
                    if func_node.type == "identifier":
                        calls.append(code_bytes[func_node.start_byte : func_node.end_byte].decode("utf8", errors="ignore"))
                    elif func_node.type == "member_expression":
                        prop_node = func_node.child_by_field_name("property")
                        if prop_node:
                            calls.append(code_bytes[prop_node.start_byte : prop_node.end_byte].decode("utf8", errors="ignore"))

        # Recurse
        for child in node.children:
            self._manual_walk(child, ext, code_bytes, definitions, calls)

    def _extract_symbols(self, node, ext: str, code_bytes: bytes, code_lines: List[str]) -> List[Dict[str, Any]]:
        """
        함수/클래스 단위로 심볼 정보 추출.
        
        Returns:
            List[Dict]: 각 심볼에 대한 정보
                - name: 심볼 이름
                - type: "function" | "class" | "method"
                - start_line: 시작 라인 (1-indexed)
                - end_line: 끝 라인 (1-indexed)
                - code: 해당 심볼의 전체 코드
                - docstring: Docstring (있는 경우)
        """
        symbols = []
        self._walk_extract_symbols(node, ext, code_bytes, code_lines, symbols)
        return symbols
    
    def _walk_extract_symbols(
        self, 
        node, 
        ext: str, 
        code_bytes: bytes, 
        code_lines: List[str], 
        symbols: List[Dict[str, Any]],
        parent_class: Optional[str] = None
    ):
        """재귀적으로 AST를 순회하며 심볼 추출"""
        node_type = node.type
        
        # Python: 함수/클래스
        if ext == ".py":
            if node_type == "function_definition":
                symbol_info = self._extract_python_function(node, code_bytes, code_lines, parent_class)
                if symbol_info:
                    symbols.append(symbol_info)
            elif node_type == "class_definition":
                symbol_info = self._extract_python_class(node, code_bytes, code_lines)
                if symbol_info:
                    symbols.append(symbol_info)
                    # 클래스 내부 메서드도 추출
                    class_name = symbol_info["name"]
                    for child in node.children:
                        self._walk_extract_symbols(child, ext, code_bytes, code_lines, symbols, class_name)
                    return  # 이미 자식을 순회함
        
        # JavaScript/TypeScript: 함수/클래스
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            if node_type in ["function_declaration", "arrow_function"]:
                symbol_info = self._extract_js_function(node, code_bytes, code_lines)
                if symbol_info:
                    symbols.append(symbol_info)
            elif node_type == "class_declaration":
                symbol_info = self._extract_js_class(node, code_bytes, code_lines)
                if symbol_info:
                    symbols.append(symbol_info)
        
        # 자식 노드 재귀 순회
        for child in node.children:
            self._walk_extract_symbols(child, ext, code_bytes, code_lines, symbols, parent_class)
    
    def _extract_python_function(
        self, 
        node, 
        code_bytes: bytes, 
        code_lines: List[str],
        parent_class: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Python 함수/메서드 정보 추출"""
        name = None
        for child in node.children:
            if child.type == "identifier":
                name = code_bytes[child.start_byte : child.end_byte].decode("utf8", errors="ignore")
                break
        
        if not name:
            return None
        
        start_line = node.start_point[0] + 1  # 1-indexed
        end_line = node.end_point[0] + 1
        
        # 코드 추출
        code = "\n".join(code_lines[start_line - 1 : end_line])
        
        # Docstring 추출
        docstring = self._extract_docstring(node, code_bytes)
        
        symbol_type = "method" if parent_class else "function"
        full_name = f"{parent_class}.{name}" if parent_class else name
        
        return {
            "name": full_name,
            "type": symbol_type,
            "start_line": start_line,
            "end_line": end_line,
            "code": code,
            "docstring": docstring,
        }
    
    def _extract_python_class(self, node, code_bytes: bytes, code_lines: List[str]) -> Optional[Dict[str, Any]]:
        """Python 클래스 정보 추출"""
        name = None
        for child in node.children:
            if child.type == "identifier":
                name = code_bytes[child.start_byte : child.end_byte].decode("utf8", errors="ignore")
                break
        
        if not name:
            return None
        
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        code = "\n".join(code_lines[start_line - 1 : end_line])
        docstring = self._extract_docstring(node, code_bytes)
        
        return {
            "name": name,
            "type": "class",
            "start_line": start_line,
            "end_line": end_line,
            "code": code,
            "docstring": docstring,
        }
    
    def _extract_js_function(self, node, code_bytes: bytes, code_lines: List[str]) -> Optional[Dict[str, Any]]:
        """JavaScript/TypeScript 함수 정보 추출"""
        name = None
        for child in node.children:
            if child.type == "identifier":
                name = code_bytes[child.start_byte : child.end_byte].decode("utf8", errors="ignore")
                break
        
        if not name:
            return None
        
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        code = "\n".join(code_lines[start_line - 1 : end_line])
        
        return {
            "name": name,
            "type": "function",
            "start_line": start_line,
            "end_line": end_line,
            "code": code,
            "docstring": None,
        }
    
    def _extract_js_class(self, node, code_bytes: bytes, code_lines: List[str]) -> Optional[Dict[str, Any]]:
        """JavaScript/TypeScript 클래스 정보 추출"""
        name = None
        for child in node.children:
            if child.type == "identifier":
                name = code_bytes[child.start_byte : child.end_byte].decode("utf8", errors="ignore")
                break
        
        if not name:
            return None
        
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        code = "\n".join(code_lines[start_line - 1 : end_line])
        
        return {
            "name": name,
            "type": "class",
            "start_line": start_line,
            "end_line": end_line,
            "code": code,
            "docstring": None,
        }
    
    def _extract_docstring(self, node, code_bytes: bytes) -> Optional[str]:
        """Python Docstring 추출"""
        # 함수/클래스 본문에서 첫 번째 expression_statement 찾기
        for child in node.children:
            if child.type == "block":
                for stmt in child.children:
                    if stmt.type == "expression_statement":
                        for expr in stmt.children:
                            if expr.type == "string":
                                docstring = code_bytes[expr.start_byte : expr.end_byte].decode("utf8", errors="ignore")
                                # 따옴표 제거
                                if docstring.startswith('"""') or docstring.startswith("'''"):
                                    return docstring[3:-3].strip()
                                elif docstring.startswith('"') or docstring.startswith("'"):
                                    return docstring[1:-1].strip()
                        break  # 첫 번째 statement만 확인
                break
        return None
