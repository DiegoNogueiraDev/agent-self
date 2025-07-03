from typing import Dict, Any
from .threshold import ThresholdPredictor
from .isolation_forest import IsolationForestPredictor
from src.logger import setup_logger

log = setup_logger(__name__)

def Predictor(config: Dict[str, Any]):
    """
    Factory function to instantiate the correct predictor based on config.
    """
    predictor_type = config.get("type", "threshold")
    log.info(f"Instantiating predictor of type: {predictor_type}")

    if predictor_type == "isolation_forest":
        return IsolationForestPredictor(config)
    elif predictor_type == "threshold":
        return ThresholdPredictor(config)
    else:
        log.error(f"Unknown predictor type: {predictor_type}. Defaulting to ThresholdPredictor.")
        return ThresholdPredictor(config)
