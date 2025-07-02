import time
from src.collector import SystemCollector
from src.predictor import Predictor
from src.logger import setup_logger

log = setup_logger("agent_main")

def main_loop():
    """
    The main operational loop of the agent.
    It collects, predicts, and will eventually trigger remediation.
    """
    log.info("Initializing Self-Healing AI Agent...")

    collector = SystemCollector()
    
    # We can pass configuration to the predictor, e.g., the threshold
    predictor_config = {"threshold": 0.85}
    predictor = Predictor(config=predictor_config)

    log.info("Agent initialized. Starting monitoring loop...")

    try:
        while True:
            # 1. Collect metrics
            metrics = collector.collect_all_metrics()
            log.debug(f"Collected metrics: {metrics}")

            # 2. Predict based on metrics
            prediction = predictor.predict(metrics)
            log.info(f"Prediction result: {prediction}")

            if prediction.get("is_anomaly"):
                log.warning(f"Anomaly detected! Score: {prediction.get('anomaly_score')}")
                # TODO: Integrate with Remediator (Task 8)

            # Wait for a defined interval before the next cycle
            time.sleep(10) # 10-second interval

    except KeyboardInterrupt:
        log.info("Agent shutting down.")
    except Exception as e:
        log.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)

if __name__ == "__main__":
    main_loop()
