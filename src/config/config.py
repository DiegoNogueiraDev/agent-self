import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .schema import AppConfig
from src.logger.logger import setup_logger

log = setup_logger(__name__)

_config_cache: Optional[AppConfig] = None

def get_config(path: str = "config/config.yaml") -> AppConfig:
    """
    Loads the configuration from a YAML file, validates it, and caches it.
    
    Args:
        path (str): The path to the YAML config file.

    Returns:
        An AppConfig instance containing the validated configuration.
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache

    config_path = Path(path)
    if not config_path.is_file():
        log.error(f"Configuration file not found at: {config_path}")
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    try:
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f) or {}
        
        config = AppConfig(**raw_config)
        _config_cache = config
        log.info("Configuration loaded and validated successfully.")
        return config
    except yaml.YAMLError as e:
        log.error(f"Error parsing YAML file: {e}")
        raise e
    except Exception as e: # Catches pydantic.ValidationError
        log.error(f"Configuration validation error: {e}")
        raise e 