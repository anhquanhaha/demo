"""
Helper functions and utilities
"""
import asyncio
from typing import Any, Callable, Optional, Dict
from functools import wraps
import time

from .logger import get_logger

logger = get_logger(__name__)


def safe_execute(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Execute function safely với error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        default: Default value nếu có lỗi
        **kwargs: Function keyword arguments
        
    Returns:
        Function result hoặc default value
        
    Examples:
        >>> result = safe_execute(int, "123", default=0)
        >>> result = safe_execute(dict.get, my_dict, "key", default="not_found")
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Error in safe_execute: {e}")
        return default


def format_response(content: str, prefix: str = "🤖", max_length: Optional[int] = None) -> str:
    """
    Format response message cho user
    
    Args:
        content: Response content
        prefix: Prefix cho message
        max_length: Max length of message (optional)
        
    Returns:
        Formatted response string
    """
    if not content:
        return f"{prefix} [Không có phản hồi]"
    
    # Truncate nếu quá dài
    if max_length and len(content) > max_length:
        content = content[:max_length-3] + "..."
    
    return f"{prefix} {content}"


def retry(max_attempts: int = 3, delay: float = 1.0, exponential_backoff: bool = False):
    """
    Decorator để retry function khi có lỗi
    
    Args:
        max_attempts: Số lần thử tối đa
        delay: Thời gian delay giữa các lần thử
        exponential_backoff: Sử dụng exponential backoff
        
    Examples:
        @retry(max_attempts=3, delay=1.0)
        def unreliable_function():
            # Function có thể fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise e
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    
                    if exponential_backoff:
                        current_delay *= 2
            
        return wrapper
    return decorator


def measure_time(func: Callable) -> Callable:
    """
    Decorator để đo thời gian execution
    
    Examples:
        @measure_time
        def slow_function():
            time.sleep(1)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"Function '{func.__name__}' took {execution_time:.2f} seconds")
        
        return result
    return wrapper


def validate_config(config: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate configuration dictionary
    
    Args:
        config: Configuration dictionary
        required_keys: List of required keys
        
    Returns:
        True nếu config valid
        
    Examples:
        >>> valid = validate_config({"api_key": "123"}, ["api_key"])
        True
    """
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        logger.error(f"Missing required config keys: {missing_keys}")
        return False
    
    return True


class Timer:
    """Context manager để đo thời gian"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"{self.name} completed in {duration:.2f} seconds")
    
    @property
    def elapsed(self) -> Optional[float]:
        """Get elapsed time"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text nếu quá dài
    
    Args:
        text: Text để truncate
        max_length: Max length
        suffix: Suffix thêm vào cuối
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def is_json_string(text: str) -> bool:
    """Check if string is valid JSON"""
    import json
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename để safe cho filesystem
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Xóa các ký tự không an toàn
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Xóa spaces ở đầu/cuối và replace multiple spaces
    sanitized = re.sub(r'\s+', ' ', sanitized.strip())
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized
