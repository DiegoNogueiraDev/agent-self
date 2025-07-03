import time
from collections import deque
from src.collector import SystemCollector
from src.predictor import Predictor
from src.config import get_config
from src.logger import setup_logger
from src.remediator import Remediator
from src.visualizer import Visualizer


def verify_remediation(collector, predictor, remediator, log) -> bool:
    """
    Checks the system state for a few cycles after a remediation action.
    """
    log.info("Entering post-remediation verification state...")
    verification_cycles = 3
    short_interval = 5  # seconds

    for i in range(verification_cycles):
        log.info(f"Verification cycle {i+1}/{verification_cycles}...")
        time.sleep(short_interval)
        
        snapshot = collector.collect()
        prediction = predictor.predict(snapshot)

        if prediction.get('is_anomaly'):
            log.warning("Anomaly still present after remediation attempt.")
            # The remediator's exclusion list will prevent immediate re-action
            # on the same PID. We can try to remediate again in case a *different*
            # root cause has emerged.
            remediator.perform_remediation(snapshot)
            return False # Verification failed

    log.info("Verification successful. Anomaly appears to be resolved.")
    return True


def main():
    """
    Main loop for the self-healing agent.
    """
    log = setup_logger(__name__)
    log.info("Starting self-healing agent...")

    config = get_config()
    interval_seconds = config.main_loop.interval_seconds
    
    collector = SystemCollector()
    predictor = Predictor(config.predictor.dict())
    remediator = Remediator(config.remediator.dict())
    visualizer = Visualizer()

    history = deque(maxlen=30)  # Store last 30 snapshots

    log.info(f"Monitoring interval set to {interval_seconds} seconds.")

    try:
        while True:
            log.debug("Collecting system metrics...")
            snapshot = collector.collect()
            history.append(snapshot)
            
            log.debug("Analyzing metrics for anomalies...")
            # Pass the system-level metrics to the predictor
            prediction = predictor.predict(snapshot.get('system', {}))

            if prediction.get('is_anomaly', False):
                log.warning("Anomaly detected! Initiating remediation and visualization.")
                
                # Visualize the metric that caused the anomaly *before* remediation
                metric_name = prediction.get("metric_checked")
                threshold = prediction.get("threshold")
                if metric_name and threshold is not None:
                    visualizer.plot_metric(
                        data=[s.get('system', {}) for s in history], 
                        metric_name=metric_name, 
                        threshold=threshold
                    )
                else:
                    log.error("Cannot visualize anomaly: metric name or threshold not found in prediction.")

                remediator.perform_remediation(snapshot)

                # Verify the outcome of the remediation
                verify_remediation(collector, predictor, remediator, log)

            else:
                log.info("System state is normal.")

            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        log.info("Agent stopped by user.")
    except Exception as e:
        log.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)

if __name__ == "__main__":
    main()
