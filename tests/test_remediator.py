import unittest
from unittest.mock import MagicMock, patch
from src.remediator.remediator import Remediator
from src.predictor.predictor import Predictor
from src.collector.collector import SystemCollector

class TestRemediatorIntegration(unittest.TestCase):

    def setUp(self):
        """Setup mock objects for testing."""
        self.mock_logger = MagicMock()
        # The predictor needs a config, let's set it for memory by default
        predictor_config = {"metric": "memory_percent", "threshold": 75.0}
        
        self.collector = SystemCollector()
        self.predictor = Predictor(config=predictor_config)
        self.remediator = Remediator()
        
        # We patch the actual kill function inside the 'actions' module
        self.mock_kill_patch = patch('src.remediator.actions.kill_process_by_pid', return_value=True)
        self.mock_kill = self.mock_kill_patch.start()

    def tearDown(self):
        """Stop the patcher."""
        self.mock_kill_patch.stop()

    def test_remediation_triggered_on_high_memory(self):
        """
        Test that the remediator kills the correct process based on high memory usage.
        """
        mock_process_list = [
            {'pid': 201, 'name': 'normal_process', 'memory_percent': 10.0},
            {'pid': 202, 'name': 'high_mem_process', 'memory_percent': 85.0}
        ]
        mock_snapshot = {
            'system': {'cpu_percent': 20.0, 'memory_percent': 80.0},
            'processes': mock_process_list
        }
        
        with patch.object(self.collector, 'collect', return_value=mock_snapshot):
            snapshot_data = self.collector.collect()
            prediction = self.predictor.predict(snapshot_data['system'])
            
            if prediction.get("is_anomaly"):
                self.remediator.perform_remediation(snapshot_data)

            # Assert kill was called once with the high-memory PID
            self.mock_kill.assert_called_once_with(202)

    def test_remediation_is_not_triggered_on_normal_usage(self):
        """
        Test that the remediator is NOT triggered when system usage is normal.
        """
        # Configure predictor for a non-anomalous scenario
        self.predictor.threshold = 95.0 

        mock_snapshot = {
            'system': {'cpu_percent': 50.0, 'memory_percent': 40.0},
            'processes': []
        }
        
        with patch.object(self.collector, 'collect', return_value=mock_snapshot):
            snapshot_data = self.collector.collect()
            prediction = self.predictor.predict(snapshot_data['system'])
            
            if prediction.get("is_anomaly"):
                self.remediator.perform_remediation(snapshot_data)

            # Assert that the kill function was NOT called
            self.mock_kill.assert_not_called()

if __name__ == '__main__':
    unittest.main()
