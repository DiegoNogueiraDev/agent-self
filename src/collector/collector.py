import psutil
import time
from typing import Dict, Any
from src.logger.logger import setup_logger

log = setup_logger(__name__)

class SystemCollector:
    """
    Collects system metrics such as CPU, memory, and disk usage.
    """

    def get_cpu_usage(self) -> Dict[str, Any]:
        """
        Gathers CPU usage statistics.
        
        Returns:
            A dictionary containing CPU usage percentage and core counts.
        """
        try:
            usage = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_count_physical": psutil.cpu_count(logical=False),
            }
            log.debug(f"Collected CPU usage: {usage}")
            return usage
        except Exception as e:
            log.error(f"Error collecting CPU usage: {e}", exc_info=True)
            return {"error": str(e)}

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Gathers virtual memory usage statistics.

        Returns:
            A dictionary containing memory stats (total, available, used, percentage).
        """
        try:
            mem = psutil.virtual_memory()
            usage = {
                "memory_total_gb": round(mem.total / (1024**3), 2),
                "memory_available_gb": round(mem.available / (1024**3), 2),
                "memory_used_gb": round(mem.used / (1024**3), 2),
                "memory_percent": mem.percent,
            }
            log.debug(f"Collected memory usage: {usage}")
            return usage
        except Exception as e:
            log.error(f"Error collecting memory usage: {e}", exc_info=True)
            return {"error": str(e)}

    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Gathers disk usage statistics for the root partition.

        Returns:
            A dictionary containing disk stats for the '/' partition.
        """
        try:
            disk = psutil.disk_usage('/')
            usage = {
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": disk.percent,
            }
            log.debug(f"Collected disk usage: {usage}")
            return usage
        except Exception as e:
            log.error(f"Error collecting disk usage: {e}", exc_info=True)
            return {"error": str(e)}

    def collect_all_metrics(self) -> Dict[str, Any]:
        """
        Collects all defined system metrics.

        Returns:
            A dictionary containing all collected metrics, timestamped.
        """
        log.info("Starting a new metric collection cycle.")
        metrics = {
            "timestamp": time.time(),
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
        }
        log.info("Finished metric collection cycle.")
        return metrics

if __name__ == '__main__':
    # Example usage:
    collector = SystemCollector()
    log.info("Starting collector example loop...")
    while True:
        metrics = collector.collect_all_metrics()
        log.info(f"Collected metrics: {metrics}")
        time.sleep(5)
