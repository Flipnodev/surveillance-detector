"""
Configuration management module.

Loads and manages application configuration from YAML file.
Provides easy access to configuration values throughout the application.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """
    Application configuration container.
    
    Provides dot-notation access to configuration values.
    Example: config.detection.min_detections
    """
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        Initialize configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary loaded from YAML
        """
        for key, value in config_dict.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with default fallback.
        
        Args:
            key: Configuration key (supports dot notation: 'detection.min_detections')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self
        
        for k in keys:
            if isinstance(value, Config):
                value = getattr(value, k, None)
            elif isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration back to dictionary.
        
        Returns:
            Configuration as nested dictionary
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Config):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config({self.to_dict()})"


class ConfigLoader:
    """
    Configuration file loader and manager.
    
    Loads YAML configuration files and provides access to configuration values.
    """
    
    _instance: Optional['ConfigLoader'] = None
    _config: Optional[Config] = None
    
    def __new__(cls):
        """Singleton pattern to ensure one configuration instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, config_path: str = 'config.yaml') -> Config:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded configuration object
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        self._config = Config(config_dict)
        return self._config
    
    def get_config(self) -> Config:
        """
        Get loaded configuration.
        
        Returns:
            Configuration object
            
        Raises:
            RuntimeError: If configuration not loaded yet
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        return self._config
    
    def reload(self, config_path: str = 'config.yaml') -> Config:
        """
        Reload configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Reloaded configuration object
        """
        return self.load(config_path)
    
    def save(self, config_path: str = 'config.yaml') -> None:
        """
        Save current configuration to file.
        
        Args:
            config_path: Path to save configuration
            
        Raises:
            RuntimeError: If no configuration loaded
        """
        if self._config is None:
            raise RuntimeError("No configuration to save")
        
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self._config.to_dict(), f, default_flow_style=False, sort_keys=False)


# Convenience functions for global access
_loader = ConfigLoader()


def load_config(config_path: str = 'config.yaml') -> Config:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration object
    """
    return _loader.load(config_path)


def get_config() -> Config:
    """
    Get current configuration.
    
    Returns:
        Configuration object
    """
    return _loader.get_config()


def reload_config(config_path: str = 'config.yaml') -> Config:
    """
    Reload configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Reloaded configuration object
    """
    return _loader.reload(config_path)