import yaml
from pathlib import Path
from typing import Dict, Any
from src.logger import setup_logger

log = setup_logger(__name__)

_config: Dict[str, Any] = None
_config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

def get_config() -> Dict[str, Any]:
    """
    Loads the configuration from config/config.yaml and returns it.
    It caches the configuration after the first read.
    """
    global _config
    if _config is not None:
        return _config

    if not _config_path.is_file():
        log.error(f"Configuration file not found at: {_config_path}")
        raise FileNotFoundError(f"Configuration file not found at: {_config_path}")

    try:
        with open(_config_path, 'r') as f:
            _config = yaml.safe_load(f)
        log.info(f"Successfully loaded configuration from {_config_path}")
        return _config
    except yaml.YAMLError as e:
        log.error(f"Error parsing YAML configuration file: {e}", exc_info=True)
        raise
    except Exception as e:
        log.error(f"An unexpected error occurred while loading configuration: {e}", exc_info=True)
        raise 