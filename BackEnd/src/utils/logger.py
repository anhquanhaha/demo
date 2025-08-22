"""
Logging utilities
"""
import logging
import sys
from typing import Optional
from pathlib import Path


def setup_logger(
    name: str = "AIAgent",
    level: str = "INFO", 
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger với cấu hình cơ bản
    
    Args:
        name: Tên logger
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Đường dẫn file log (optional)
        format_string: Custom format string (optional)
        
    Returns:
        Configured logger instance
    """
    
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "AIAgent") -> logging.Logger:
    """
    Get existing logger hoặc tạo logger mới với default config
    
    Args:
        name: Tên logger
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # Nếu chưa có handler thì setup với default config
    if not logger.handlers:
        logger = setup_logger(name)
    
    return logger
