"""
Synapse 커스텀 예외 클래스.

모든 Synapse 관련 에러를 일관되게 처리합니다.
"""


class SynapseError(Exception):
    """Synapse 기본 예외 클래스"""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class ParserError(SynapseError):
    """파싱 관련 에러"""
    
    def __init__(self, file_path: str, message: str, line: int = None):
        details = {"file": file_path}
        if line:
            details["line"] = line
        super().__init__(f"파싱 실패 [{file_path}]: {message}", details)


class IndexingError(SynapseError):
    """인덱싱 관련 에러"""
    
    def __init__(self, message: str, file_count: int = None):
        details = {}
        if file_count:
            details["file_count"] = file_count
        super().__init__(f"인덱싱 실패: {message}", details)


class GraphError(SynapseError):
    """의존성 그래프 관련 에러"""
    
    def __init__(self, message: str, node: str = None):
        details = {}
        if node:
            details["node"] = node
        super().__init__(f"그래프 오류: {message}", details)


class SearchError(SynapseError):
    """검색 관련 에러"""
    
    def __init__(self, query: str, message: str):
        details = {"query": query}
        super().__init__(f"검색 실패 [{query}]: {message}", details)


class ConfigError(SynapseError):
    """설정 관련 에러"""
    
    def __init__(self, message: str, config_key: str = None):
        details = {}
        if config_key:
            details["key"] = config_key
        super().__init__(f"설정 오류: {message}", details)


class WatcherError(SynapseError):
    """File Watcher 관련 에러"""
    
    def __init__(self, message: str, path: str = None):
        details = {}
        if path:
            details["path"] = path
        super().__init__(f"Watcher 오류: {message}", details)
