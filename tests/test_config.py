import pytest
import yaml
from unittest.mock import mock_open, patch
from src.config.config import get_config, AppConfig
from pydantic import ValidationError

@pytest.fixture(autouse=True)
def clear_config_cache():
    """Fixture to clear the config cache before each test."""
    with patch('src.config.config._config_cache', None):
        yield

def test_get_config_success(mocker):
    """
    Test successful loading and parsing of a YAML config file.
    """
    yaml_content = """
main_loop:
  interval_seconds: 15
predictor:
  threshold: 0.9
"""
    mocker.patch("builtins.open", mock_open(read_data=yaml_content))
    mocker.patch("pathlib.Path.is_file", return_value=True)
    
    config = get_config(path="dummy/path/config.yaml")
    
    assert isinstance(config, AppConfig)
    assert config.main_loop.interval_seconds == 15
    assert config.predictor.threshold == 0.9
    assert config.logging.level == 'INFO' # Check default

def test_get_config_file_not_found(mocker):
    """
    Test that FileNotFoundError is raised when the config file doesn't exist.
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)
    
    with pytest.raises(FileNotFoundError):
        get_config(path="non/existent/path.yaml")

def test_get_config_caching(mocker):
    """
    Test that the configuration is cached after the first read.
    """
    yaml_content = "main_loop: {interval_seconds: 10}"
    
    mock_file = mock_open(read_data=yaml_content)
    mocker.patch("builtins.open", mock_file)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    config1 = get_config(path="cached/path.yaml")
    config2 = get_config(path="cached/path.yaml")

    assert isinstance(config1, AppConfig)
    assert config1.main_loop.interval_seconds == 10
    assert config2 is config1
    mock_file.assert_called_once()

def test_get_config_validation_error(mocker):
    """
    Test that a validation error is raised for invalid config values.
    """
    invalid_yaml_content = "main_loop: {interval_seconds: -5}" # Must be > 0
    
    mocker.patch("builtins.open", mock_open(read_data=invalid_yaml_content))
    mocker.patch("pathlib.Path.is_file", return_value=True)
    
    with pytest.raises(ValidationError):
        get_config(path="invalid/path.yaml")

def test_get_config_yaml_error(mocker):
    """
    Test that a YAMLError is raised for a malformed YAML file.
    """
    invalid_yaml_content = "key:\n\t- value"
    
    mocker.patch("builtins.open", mock_open(read_data=invalid_yaml_content))
    mocker.patch("pathlib.Path.is_file", return_value=True)
    
    with pytest.raises(yaml.YAMLError):
        get_config(path="malformed/path.yaml") 