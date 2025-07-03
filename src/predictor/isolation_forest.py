from typing import Dict, Any
import joblib
from src.logger.logger import setup_logger
from .base import BasePredictor

log = setup_logger(__name__)

class IsolationForestPredictor(BasePredictor):
    """
    A predictor that uses a trained Isolation Forest model to detect anomalies.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.model_path = self.config.get("model_path")
        if not self.model_path:
            log.error("IsolationForestPredictor: 'model_path' not found in configuration.")
            raise ValueError("Model path must be specified for IsolationForestPredictor.")
        self.load_model()

    def load_model(self) -> None:
        """
        Loads the Isolation Forest model from the specified path.
        """
        try:
            self.model = joblib.load(self.model_path)
            log.info(f"IsolationForest model loaded successfully from {self.model_path}")
        except FileNotFoundError:
            log.error(f"IsolationForest model file not found at {self.model_path}")
            raise
        except Exception as e:
            log.error(f"An error occurred while loading the model: {e}")
            raise

    def predict(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses the loaded model to predict if the metrics represent an anomaly.

        Args:
            metrics (Dict[str, Any]): System metrics.

        Returns:
            A dictionary containing the prediction result.
        """
        if not self.model:
            log.warning("IsolationForestPredictor: No model loaded. Cannot perform prediction.")
            return {"is_anomaly": False, "reason": "No model loaded"}

        try:
            features_to_use = ['cpu_percent', 'memory_percent']
            feature_vector = [metrics.get(f, 0) for f in features_to_use]
            data_for_prediction = [feature_vector] 

            prediction = self.model.predict(data_for_prediction)
            
            is_anomaly = prediction[0] == -1
            
            log.info(f"Prediction result: {'Anomaly' if is_anomaly else 'Normal'}")

            return {
                "is_anomaly": is_anomaly,
                "raw_prediction": int(prediction[0]),
                "features_used": features_to_use,
                "feature_values": feature_vector
            }

        except Exception as e:
            log.error(f"An error occurred during prediction: {e}")
            return {"is_anomaly": False, "reason": f"Prediction error: {e}"} 