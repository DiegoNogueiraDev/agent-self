import pytest
import yaml
from unittest.mock import mock_open, patch
from src.config.config import get_config

@pytest.fixture(autouse=True)
def clear_config_cache():
    """Fixture to clear the config cache before each test."""
    # To be precise, we need to patch the internal cache of the config module
    with patch('src.config.config._config_cache', {}):
        yield

def test_get_config_success(mocker):
    """
    Test successful loading and parsing of a YAML config file.
    """
    yaml_content = "key: value"
    mocker.patch("builtins.open", mock_open(read_data=yaml_content))
    mocker.patch("pathlib.Path.is_file", return_value=True)
    
    config = get_config(path="dummy/path/config.yaml")
    
    assert config == {"key": "value"}

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
    yaml_content = "key: value"
    
    # Mock open to be called only once
    mock_file = mock_open(read_data=yaml_content)
    mocker.patch("builtins.open", mock_file)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    # First call - should read the file
    config1 = get_config(path="cached/path.yaml")
    # Second call - should use the cache
    config2 = get_config(path="cached/path.yaml")

    assert config1 == {"key": "value"}
    assert config2 == config1
    # Check that open was called exactly once. We don't need to assert the args
    # in this case as it gets complicated with the Path object.
    mock_file.assert_called_once()


def test_get_config_yaml_error(mocker):
    """
    Test that a YAMLError is raised for a malformed YAML file.
    """
    # Invalid YAML (a tab character is not allowed for indentation)
    invalid_yaml_content = "key:\n\t- value"
    
    mocker.patch("builtins.open", mock_open(read_data=invalid_yaml_content))
    mocker.patch("pathlib.Path.is_file", return_value=True)
    
    with pytest.raises(yaml.YAMLError):
        get_config(path="malformed/path.yaml") 