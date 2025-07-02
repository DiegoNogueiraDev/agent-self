from .base import BasePredictor
from typing import Dict, Any
import random
from src.logger.logger import setup_logger

log = setup_logger(__name__)

class MockPredictor(BasePredictor):
    """
    A mock predictor for testing and development.
    It returns a random anomaly score.
    """

    def load_model(self) -> None:
        """
        Mock model loading. Does nothing.
        """
        log.info("MockPredictor: 'Loading' mock model.")
        pass

    def predict(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a mock prediction.

        Args:
            metrics (Dict[str, Any]): System metrics (ignored in mock).

        Returns:
            A dictionary with a random anomaly score.
        """
        log.debug(f"MockPredictor: Received metrics for prediction: {metrics}")
        
        # In a real scenario, this would be a sophisticated calculation.
        # Here, we just generate a random float between 0.0 and 1.0.
        anomaly_score = random.uniform(0.0, 1.0)
        
        prediction = {
            "anomaly_score": anomaly_score,
            "is_anomaly": anomaly_score > self.config.get("threshold", 0.8)
        }
        
        log.info(f"MockPredictor: Generated prediction: {prediction}")
        return prediction

# For now, the main Predictor class will just be an alias for the MockPredictor
# until we implement the real one.
Predictor = MockPredictor
