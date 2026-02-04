"""
Synapse 로깅 시스템.

통합 로거를 제공하여 일관된 로깅을 지원합니다.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# 로그 포맷 정의
CONSOLE_FORMAT = "%(levelname)s: %(message)s"
FILE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DEBUG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"


class SynapseLogger:
    """Synapse 통합 로거"""
    
    _instance: Optional["SynapseLogger"] = None
    _initialized: bool = False
    
    def __new__(cls, *args, **kwargs):
        """싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        name: str = "synapse",
        level: int = logging.INFO,
        log_dir: Optional[Path] = None,
        verbose: bool = False,
        quiet: bool = False
    ):
        # 이미 초기화됐으면 스킵
        if SynapseLogger._initialized:
            return
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # 핸들러에서 필터링
        self.logger.handlers.clear()  # 기존 핸들러 제거
        
        # 콘솔 레벨 결정
        if quiet:
            console_level = logging.ERROR
        elif verbose:
            console_level = logging.DEBUG
        else:
            console_level = logging.INFO
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(logging.Formatter(
            DEBUG_FORMAT if verbose else CONSOLE_FORMAT
        ))
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 (log_dir이 있을 때만)
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 날짜별 로그 파일
            log_file = log_dir / f"synapse_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(FILE_FORMAT))
            self.logger.addHandler(file_handler)
        
        SynapseLogger._initialized = True
    
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        """예외 정보와 함께 에러 로깅"""
        self.logger.exception(msg, *args, **kwargs)
    
    @classmethod
    def reset(cls):
        """싱글톤 리셋 (테스트용)"""
        if cls._instance:
            cls._instance.logger.handlers.clear()
        cls._instance = None
        cls._initialized = False


def get_logger(
    name: str = "synapse",
    verbose: bool = False,
    quiet: bool = False,
    log_dir: Optional[Path] = None
) -> SynapseLogger:
    """로거 인스턴스 가져오기"""
    return SynapseLogger(
        name=name,
        verbose=verbose,
        quiet=quiet,
        log_dir=log_dir
    )


# 기본 로거 (빠른 접근용)
def debug(msg: str, *args, **kwargs):
    get_logger().debug(msg, *args, **kwargs)

def info(msg: str, *args, **kwargs):
    get_logger().info(msg, *args, **kwargs)

def warning(msg: str, *args, **kwargs):
    get_logger().warning(msg, *args, **kwargs)

def error(msg: str, *args, **kwargs):
    get_logger().error(msg, *args, **kwargs)

def exception(msg: str, *args, **kwargs):
    get_logger().exception(msg, *args, **kwargs)
