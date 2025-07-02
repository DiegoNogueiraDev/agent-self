import pytest
from unittest.mock import patch, MagicMock
from src.collector.collector import SystemCollector

@pytest.fixture
def mocked_psutil(mocker):
    """Mocks psutil functions for predictable test outcomes."""
    mocker.patch('psutil.cpu_percent', return_value=15.5)
    mocker.patch('psutil.virtual_memory', return_value=MagicMock(percent=55.5))
    
    # Mock for process_iter
    mock_proc = MagicMock()
    mock_proc.info = {
        'pid': 1, 'name': 'test_proc', 'username': 'testuser',
        'cpu_percent': 10.0, 'memory_percent': 5.0, 'status': 'running'
    }
    mocker.patch('psutil.process_iter', return_value=[mock_proc])

def test_collect_success(mocked_psutil):
    """
    Test successful collection of system and process metrics.
    """
    collector = SystemCollector()
    metrics = collector.collect()

    assert 'timestamp' in metrics
    assert 'error' not in metrics

    # Check system metrics
    assert 'system' in metrics
    assert metrics['system']['cpu_percent'] == 15.5
    assert metrics['system']['memory_percent'] == 55.5

    # Check process metrics
    assert 'processes' in metrics
    assert len(metrics['processes']) == 1
    assert metrics['processes'][0]['name'] == 'test_proc'

def test_collect_handles_exception(mocker):
    """
    Test that the collect method handles exceptions gracefully and returns an error dict.
    """
    mocker.patch('psutil.cpu_percent', side_effect=RuntimeError("A psutil error occurred"))
    
    collector = SystemCollector()
    metrics = collector.collect()

    assert 'timestamp' in metrics
    assert 'error' in metrics
    assert "A psutil error occurred" in metrics['error']
    assert 'system' in metrics
    assert 'processes' in metrics
