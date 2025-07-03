from typing import Dict, Any
from src.logger.logger import setup_logger
from .base import BasePredictor

log = setup_logger(__name__)

class ThresholdPredictor(BasePredictor):
    """
    A simple predictor that triggers an anomaly if a metric exceeds a threshold.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.metric_to_check = self.config.get("metric", "memory_percent")
        self.threshold = self.config.get("threshold", 0.8)
        log.info(f"ThresholdPredictor initialized. Checking metric '{self.metric_to_check}' against threshold '{self.threshold}'.")

    def load_model(self) -> None:
        """
        No model to load for this simple predictor.
        """
        log.info("ThresholdPredictor: No model to load.")
        pass

    def predict(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Checks if the configured metric exceeds the threshold.

        Args:
            metrics (Dict[str, Any]): System metrics.

        Returns:
            A dictionary containing the prediction result.
        """
        log.debug(f"ThresholdPredictor: Received metrics for prediction: {metrics}")
        
        current_value = metrics.get(self.metric_to_check, 0)
        is_anomaly = current_value > self.threshold
        
        prediction = {
            "metric_checked": self.metric_to_check,
            "current_value": current_value,
            "threshold": self.threshold,
            "is_anomaly": is_anomaly
        }
        
        if is_anomaly:
            log.warning(f"ThresholdPredictor: Anomaly detected! {prediction}")
        else:
            log.info(f"ThresholdPredictor: No anomaly detected. {prediction}")
            
        return prediction 