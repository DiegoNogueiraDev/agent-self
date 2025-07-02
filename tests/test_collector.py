import pytest
from unittest.mock import patch
from src.collector.collector import SystemCollector

@pytest.fixture
def collector():
    """Provides a SystemCollector instance for tests."""
    return SystemCollector()

def test_collect_all_metrics_success(collector, mocker):
    """
    Test that all metrics are collected successfully under normal conditions.
    """
    # Mock the underlying psutil functions to return predictable values
    mocker.patch('psutil.cpu_percent', return_value=10.0)
    mocker.patch('psutil.cpu_count', side_effect=[8, 4]) # logical, then physical
    mocker.patch('psutil.virtual_memory', return_value=mocker.MagicMock(total=16*1024**3, available=8*1024**3, used=8*1024**3, percent=50.0))
    mocker.patch('psutil.disk_usage', return_value=mocker.MagicMock(total=500*1024**3, used=250*1024**3, free=250*1024**3, percent=50.0))

    metrics = collector.collect_all_metrics()

    assert "error" not in metrics["cpu"]
    assert "error" not in metrics["memory"]
    assert "error" not in metrics["disk"]
    assert metrics["cpu"]["cpu_percent"] == 10.0
    assert metrics["memory"]["memory_percent"] == 50.0
    assert metrics["disk"]["disk_percent"] == 50.0

def test_get_cpu_usage_error(collector, mocker):
    """
    Test that CPU collection handles exceptions gracefully.
    """
    # Mock psutil.cpu_percent to raise an exception
    mocker.patch('psutil.cpu_percent', side_effect=RuntimeError("Test CPU Error"))
    
    # Mock the logger to capture log messages
    mock_log = mocker.patch('src.collector.collector.log')

    cpu_metrics = collector.get_cpu_usage()

    assert "error" in cpu_metrics
    assert cpu_metrics["error"] == "Test CPU Error"
    
    # Verify that an error was logged
    mock_log.error.assert_called_once()
    call_args, _ = mock_log.error.call_args
    assert "Error collecting CPU usage" in call_args[0]


def test_get_memory_usage_error(collector, mocker):
    """
    Test that memory collection handles exceptions gracefully.
    """
    mocker.patch('psutil.virtual_memory', side_effect=RuntimeError("Test Memory Error"))
    mock_log = mocker.patch('src.collector.collector.log')

    mem_metrics = collector.get_memory_usage()

    assert "error" in mem_metrics
    assert mem_metrics["error"] == "Test Memory Error"
    mock_log.error.assert_called_once()
    call_args, _ = mock_log.error.call_args
    assert "Error collecting memory usage" in call_args[0]


def test_get_disk_usage_error(collector, mocker):
    """
    Test that disk collection handles exceptions gracefully.
    """
    mocker.patch('psutil.disk_usage', side_effect=RuntimeError("Test Disk Error"))
    mock_log = mocker.patch('src.collector.collector.log')
    
    disk_metrics = collector.get_disk_usage()

    assert "error" in disk_metrics
    assert disk_metrics["error"] == "Test Disk Error"
    mock_log.error.assert_called_once()
    call_args, _ = mock_log.error.call_args
    assert "Error collecting disk usage" in call_args[0]
