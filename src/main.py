import time
from src.collector import SystemCollector
from src.predictor import MockPredictor
from src.config import get_config
from src.logger import setup_logger
from src.remediator import analyze_root_cause


def main():
    """
    Main loop for the self-healing agent.
    """
    log = setup_logger(__name__)
    log.info("Starting self-healing agent...")

    config = get_config()
    main_loop_config = config.get("main_loop", {})
    interval_seconds = main_loop_config.get("interval_seconds", 60)
    
    collector = SystemCollector()
    predictor = MockPredictor()

    log.info(f"Monitoring interval set to {interval_seconds} seconds.")

    try:
        while True:
            log.debug("Collecting system metrics...")
            snapshot = collector.collect()
            
            log.debug("Analyzing metrics for anomalies...")
            prediction = predictor.predict(snapshot)

            if prediction.get('is_anomaly', False):
                log.warning("Anomaly detected! Initiating root cause analysis.")
                
                # Analyze the snapshot that triggered the anomaly
                top_offenders = analyze_root_cause(snapshot['processes'])
                
                if top_offenders:
                    log.warning(f"Top memory offenders: {[p['name'] for p in top_offenders]}")
                    # In a future task, we would take action here.
                else:
                    log.warning("RCA did not identify specific offending processes.")

            else:
                log.info("System state is normal.")

            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        log.info("Agent stopped by user.")
    except Exception as e:
        log.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)

if __name__ == "__main__":
    main()
