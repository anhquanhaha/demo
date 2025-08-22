"""
Configuration management
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
import json


class Config:
    """Configuration manager cho AI Agent"""
    
    def __init__(self):
        self.config = self._load_default_config()
        self._load_from_env()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            # LLM settings
            "llm": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.1,
                "max_tokens": None,
                "timeout": 30
            },
            
            # Agent settings  
            "agent": {
                "name": "AIAgent",
                "max_iterations": 10,
                "enable_memory": True,
                "default_thread_id": "default"
            },
            
            # Tools settings
            "tools": {
                "enable_calculator": True,
                "enable_weather": True,
                "enable_time": True
            },
            
            # App settings
            "app": {
                "log_level": "INFO",
                "debug": False,
                "default_mode": "interactive"
            },
            
            # API settings
            "api": {
                "openai_api_key": None,
                "weather_api_key": None,
                "timeout": 30
            }
        }
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # OpenAI API Key
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.config["api"]["openai_api_key"] = openai_key
        
        # Debug mode
        debug = os.getenv("DEBUG", "false").lower() == "true"
        self.config["app"]["debug"] = debug
        
        # Log level
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.config["app"]["log_level"] = log_level
        
        # LLM Model
        model = os.getenv("LLM_MODEL")
        if model:
            self.config["llm"]["model"] = model
        
        # Temperature  
        temp = os.getenv("LLM_TEMPERATURE")
        if temp:
            try:
                self.config["llm"]["temperature"] = float(temp)
            except ValueError:
                pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'llm.model')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Examples:
            >>> config.get('llm.model')
            'gpt-3.5-turbo'
            >>> config.get('tools.enable_calculator')
            True
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured"""
        key = self.get("api.openai_api_key")
        return key is not None and key.strip() != ""
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get("app.debug", False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self.config.copy()
    
    def load_from_file(self, filepath: str) -> None:
        """Load configuration from JSON file"""
        path = Path(filepath)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
            except Exception as e:
                print(f"Warning: Could not load config from {filepath}: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing"""
        def merge_dicts(base: Dict, new: Dict) -> Dict:
            for key, value in new.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value
            return base
        
        merge_dicts(self.config, new_config)


# Global config instance
_config_instance: Optional[Config] = None


def load_config(filepath: Optional[str] = None) -> Config:
    """
    Load global configuration instance
    
    Args:
        filepath: Optional path to config file
        
    Returns:
        Config instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config()
    
    if filepath:
        _config_instance.load_from_file(filepath)
    
    return _config_instance


def get_config() -> Config:
    """Get global configuration instance"""
    if _config_instance is None:
        return load_config()
    return _config_instance
