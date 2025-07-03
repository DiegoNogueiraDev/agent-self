import pytest
from src.remediator.remediator import analyze_root_cause
from src.remediator.remediator import Remediator
from unittest.mock import patch, MagicMock
import time

@pytest.fixture
def sample_processes():
    """Provides a sample list of process data for testing."""
    return [
        {'pid': 101, 'name': 'proc_low', 'memory_percent': 1.5},
        {'pid': 102, 'name': 'proc_high', 'memory_percent': 15.0},
        {'pid': 103, 'name': 'proc_mid', 'memory_percent': 7.2},
        {'pid': 104, 'name': 'proc_highest', 'memory_percent': 25.5},
        {'pid': 105, 'name': 'proc_zero', 'memory_percent': 0.0},
        {'pid': 106, 'name': 'proc_another_low', 'memory_percent': 1.8},
    ]

def test_analyze_root_cause_success(sample_processes):
    """
    Test that the function correctly identifies and sorts the top N processes.
    """
    top_3 = analyze_root_cause(sample_processes, top_n=3)
    
    assert len(top_3) == 3
    assert top_3[0]['name'] == 'proc_highest'
    assert top_3[1]['name'] == 'proc_high'
    assert top_3[2]['name'] == 'proc_mid'
    assert [p['pid'] for p in top_3] == [104, 102, 103]

def test_analyze_root_cause_empty_list():
    """
    Test that the function returns an empty list when given an empty snapshot.
    """
    assert analyze_root_cause([]) == []

def test_analyze_root_cause_top_n_larger_than_list(sample_processes):
    """
    Test that the function returns all processes if top_n is larger than the list size.
    """
    all_procs = analyze_root_cause(sample_processes, top_n=10)
    assert len(all_procs) == len(sample_processes)
    assert all_procs[0]['name'] == 'proc_highest'

def test_analyze_root_cause_malformed_data():
    """
    Test that the function handles malformed data gracefully.
    """
    malformed_list = [
        {'pid': 201, 'name': 'valid_proc', 'memory_percent': 10.0},
        {'pid': 202, 'name': 'no_mem_key'},
        'not_a_dict'
    ]
    
    top_processes = analyze_root_cause(malformed_list)
    
    # It should ignore non-dict entries and process dicts, even if they
    # are missing the 'memory_percent' key (treating it as 0).
    assert len(top_processes) == 2
    assert top_processes[0]['name'] == 'valid_proc'

def test_analyze_root_cause_missing_memory_key():
    """
    Test that entries without 'memory_percent' are treated as zero.
    """
    processes = [
        {'pid': 301, 'name': 'proc_a', 'memory_percent': 10.0},
        {'pid': 302, 'name': 'proc_b'}, # Missing key
    ]
    top_processes = analyze_root_cause(processes)
    assert len(top_processes) == 2
    assert top_processes[0]['pid'] == 301
    assert top_processes[1]['pid'] == 302

class TestRemediator:

    @patch('src.remediator.remediator.kill_process_by_pid')
    def test_remediation_adds_to_exclusion_list(self, mock_kill, sample_processes):
        """
        Test that after a remediation action, the PID is added to the exclusion list.
        """
        mock_kill.return_value = True  # Simulate successful kill
        remediator = Remediator()
        snapshot = {'processes': sample_processes}

        offending_pid = 104
        assert offending_pid not in remediator.exclusion_list

        remediator.perform_remediation(snapshot)

        mock_kill.assert_called_once_with(offending_pid)
        assert offending_pid in remediator.exclusion_list

    @patch('src.remediator.remediator.kill_process_by_pid')
    def test_exclusion_list_prevents_remediation(self, mock_kill, sample_processes):
        """
        Test that a PID on the exclusion list is not actioned on again.
        """
        mock_kill.return_value = True
        remediator = Remediator()
        snapshot = {'processes': sample_processes}
        offending_pid = 104

        # First run: remediate and add to exclusion list
        remediator.perform_remediation(snapshot)
        mock_kill.assert_called_once_with(offending_pid)
        assert offending_pid in remediator.exclusion_list

        # Second run: the PID is on the exclusion list, so the next offender is picked.
        remediator.perform_remediation(snapshot)
        
        # Assert that kill was called again, but for the next offender (102)
        assert mock_kill.call_count == 2
        mock_kill.assert_any_call(102)

    def test_cleanup_exclusion_list(self):
        """
        Test that expired PIDs are removed from the exclusion list.
        """
        remediator = Remediator()
        remediator.exclusion_list = {
            101: time.time() - 301,  # Expired
            102: time.time() + 300   # Not expired
        }
        
        remediator._cleanup_exclusion_list()
        
        assert 101 not in remediator.exclusion_list
        assert 102 in remediator.exclusion_list
