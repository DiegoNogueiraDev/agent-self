import yaml
from pathlib import Path
from typing import Dict, Any

_config_cache: Dict[str, Any] = {}

def get_config(path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Loads the configuration from a YAML file and caches it.
    
    Args:
        path (str): The path to the YAML config file.

    Returns:
        A dictionary containing the configuration.
    """
    global _config_cache
    
    if path in _config_cache:
        return _config_cache[path]

    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            _config_cache[path] = config
            # Logging should be done by the caller, not the config loader.
            return config
    except yaml.YAMLError as e:
        # Let the caller handle the error and logging.
        raise e 