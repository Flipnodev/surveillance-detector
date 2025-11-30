"""
Logging configuration for surveillance detection system.

Provides structured logging with file and console handlers,
rotating log files, and color-coded console output.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color-coded log levels for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record with colors for console output."""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class Logger:
    """
    Centralized logging manager for the surveillance detection system.
    
    Features:
    - Dual output: console and rotating file
    - Color-coded console messages
    - Automatic log directory creation
    - Rotating file handler (10MB per file, 5 backups)
    """
    
    _instance: Optional['Logger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger (only once)."""
        if Logger._initialized:
            return
        
        self.logger = logging.getLogger('SurveillanceDetector')
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        Logger._initialized = True
    
    def setup(self, 
              log_dir: str = 'outputs/logs',
              console_level: int = logging.INFO,
              file_level: int = logging.DEBUG) -> logging.Logger:
        """
        Set up logging with console and file handlers.
        
        Args:
            log_dir: Directory for log files
            console_level: Minimum level for console output
            file_level: Minimum level for file output
            
        Returns:
            Configured logger instance
        """
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Console handler with color
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = log_path / f"surveillance_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Logging initialized - File: {log_file}")
        return self.logger
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger


# Convenience function for getting logger
def get_logger() -> logging.Logger:
    """
    Get or create the application logger.
    
    Returns:
        Configured logger instance
    """
    return Logger().get_logger()


# Convenience function for setup
def setup_logging(log_dir: str = 'outputs/logs', 
                  console_level: int = logging.INFO,
                  file_level: int = logging.DEBUG) -> logging.Logger:
    """
    Initialize logging system.
    
    Args:
        log_dir: Directory for log files
        console_level: Minimum level for console output
        file_level: Minimum level for file output
        
    Returns:
        Configured logger instance
    """
    return Logger().setup(log_dir, console_level, file_level)