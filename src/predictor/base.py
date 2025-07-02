from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePredictor(ABC):
    """
    Abstract base class for all predictor implementations.
    Defines the standard interface for prediction models.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initializes the predictor, optionally with a configuration.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters. Defaults to None.
        """
        self.config = config or {}
        self.load_model()

    @abstractmethod
    def load_model(self) -> None:
        """
        Abstract method to load the prediction model.
        This should handle loading model files, weights, etc.
        """
        pass

    @abstractmethod
    def predict(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method to perform a prediction based on input metrics.

        Args:
            metrics (Dict[str, Any]): A dictionary of system metrics from the collector.

        Returns:
            A dictionary containing the prediction result, e.g., an anomaly score.
        """
        pass 