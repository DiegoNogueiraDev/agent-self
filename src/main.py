import time
from src.collector import SystemCollector
from src.predictor import Predictor
from src.logger import setup_logger
from src.config import get_config

log = setup_logger("agent_main")

def main_loop():
    """
    The main operational loop of the agent.
    It collects, predicts, and will eventually trigger remediation.
    """
    log.info("Initializing Self-Healing AI Agent...")
    
    try:
        config = get_config()
        log.info(f"Configuration loaded: {config}")

        collector = SystemCollector()
        
        # Pass the predictor-specific config to the predictor
        predictor_config = config.get("predictor", {})
        predictor = Predictor(config=predictor_config)

        main_loop_config = config.get("main_loop", {})
        interval = main_loop_config.get("interval_seconds", 10)

        log.info(f"Agent initialized. Starting monitoring loop with {interval}s interval...")

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

            # Wait for the configured interval before the next cycle
            time.sleep(interval)

    except FileNotFoundError:
        log.error("Configuration file not found. Please ensure 'config/config.yaml' exists.")
    except KeyboardInterrupt:
        log.info("Agent shutting down.")
    except Exception as e:
        log.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)

if __name__ == "__main__":
    main_loop()
