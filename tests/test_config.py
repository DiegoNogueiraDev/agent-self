import pytest
import yaml
from unittest.mock import patch, mock_open
from src.config import get_config

@pytest.fixture(autouse=True)
def reset_config_cache():
    """
    Fixture to automatically reset the config cache before each test.
    This prevents state from leaking between tests.
    """
    # This import is local to avoid circular dependency issues at module level
    from src.config import config
    config._config = None
    yield
    config._config = None


def test_get_config_success(mocker):
    """
    Test that the config is loaded and parsed correctly from a valid YAML file.
    """
    yaml_content = """
    predictor:
      threshold: 0.9
    main_loop:
      interval_seconds: 5
    """
    
    # Mock the open call to return our fake YAML content
    mocker.patch("builtins.open", mock_open(read_data=yaml_content))
    # Mock Path.is_file() to return True
    mocker.patch("pathlib.Path.is_file", return_value=True)

    config = get_config()

    assert config is not None
    assert config["predictor"]["threshold"] == 0.9
    assert config["main_loop"]["interval_seconds"] == 5

def test_get_config_file_not_found(mocker):
    """
    Test that a FileNotFoundError is raised if the config file does not exist.
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)

    with pytest.raises(FileNotFoundError):
        get_config()

def test_get_config_yaml_error(mocker):
    """
    Test that a YAMLError is raised for a malformed YAML file.
    """
    # Invalid YAML (a tab character is not allowed for indentation)
    invalid_yaml_content = "key:\n\t- value"
    
    mocker.patch("builtins.open", mock_open(read_data=invalid_yaml_content))
    mocker.patch("pathlib.Path.is_file", return_value=True)

    with pytest.raises(yaml.YAMLError):
        get_config()

def test_config_caching(mocker):
    """
    Test that the configuration is cached after the first successful read.
    """
    yaml_content = "key: value"
    
    # Mock open and is_file to be called only once
    mocked_open = mocker.patch("builtins.open", mock_open(read_data=yaml_content))
    mocker.patch("pathlib.Path.is_file", return_value=True)

    # First call should read the file
    config1 = get_config()
    assert config1 == {"key": "value"}
    mocked_open.assert_called_once()

    # Second call should return the cached config without reading the file again
    config2 = get_config()
    assert config2 == {"key": "value"}
    mocked_open.assert_called_once() # The call count should still be 1 