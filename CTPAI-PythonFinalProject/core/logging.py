"""
Centralized logging system for the Object Detection application.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from .config import get_config

console = Console()


class LoggerManager:
    """Manages logging configuration and setup."""
    
    def __init__(self):
        """Initialize the logger manager."""
        self._loggers = {}
        self._initialized = False
    
    def setup_logging(self) -> None:
        """Setup logging configuration based on config."""
        if self._initialized:
            return
        
        config = get_config()
        log_config = config.logging
        
        # Create logs directory
        log_file_path = Path(log_config.file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_config.level))
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_config.file,
            maxBytes=log_config.max_file_size,
            backupCount=log_config.backup_count,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(log_config.format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler with Rich formatting
        if log_config.console_output:
            console_handler = RichHandler(
                console=console,
                show_time=True,
                show_path=True,
                markup=True,
                rich_tracebacks=True
            )
            console_formatter = logging.Formatter("%(message)s")
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        self._initialized = True
        logging.info("Logging system initialized")
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance."""
        if not self._initialized:
            self.setup_logging()
        
        logger_name = name or __name__
        
        if logger_name not in self._loggers:
            logger = logging.getLogger(logger_name)
            self._loggers[logger_name] = logger
        
        return self._loggers[logger_name]
    
    def set_level(self, level: str) -> None:
        """Change logging level for all loggers."""
        log_level = getattr(logging, level.upper())
        logging.getLogger().setLevel(log_level)
        
        for logger in self._loggers.values():
            logger.setLevel(log_level)


# Global logger manager instance
logger_manager = LoggerManager()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    return logger_manager.get_logger(name)


def setup_logging() -> None:
    """Setup logging system."""
    logger_manager.setup_logging()


def set_log_level(level: str) -> None:
    """Set logging level."""
    logger_manager.set_level(level) 