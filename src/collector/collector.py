import psutil
import time
from typing import Dict, Any
from src.logger import setup_logger

class SystemCollector:
    """
    Collects system-level metrics using psutil, including overall system stats
    and a detailed list of running processes.
    """

    def __init__(self):
        """Initializes the SystemCollector."""
        self.logger = setup_logger(__name__)
        # Prime all process CPU counters on initialization.
        # This is a requirement for psutil to return a non-zero CPU percentage
        # on the first meaningful call.
        for proc in psutil.process_iter(['pid']):
            try:
                p = psutil.Process(proc.info['pid'])
                p.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.logger.info("SystemCollector initialized and process CPU counters primed.")

    def collect(self) -> Dict[str, Any]:
        """
        Collects system-wide metrics (CPU, memory) and a list of process details.

        Returns:
            A dictionary containing the timestamp, system-wide metrics, and a
            list of process metric dictionaries.
        """
        self.logger.debug("Starting metric collection cycle.")
        
        try:
            # First, iterate over all processes to start the cpu_percent calculation window.
            # The first call to cpu_percent for a process is always 0.0.
            for proc in psutil.process_iter(['cpu_percent']):
                pass
            
            # Wait for a short interval for CPU usage to be measured.
            time.sleep(1)

            # System-wide metrics (now without interval, as we waited)
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent
            }
            
            # Now, collect per-process metrics. The cpu_percent will be accurate
            # for the interval we just slept.
            processes = []
            process_iter = psutil.process_iter([
                'pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status'
            ])
            
            for proc in process_iter:
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            all_metrics = {
                'timestamp': time.time(),
                'system': system_metrics,
                'processes': processes
            }

            self.logger.debug(f"Collected metrics for {len(processes)} processes.")
            return all_metrics

        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}", exc_info=True)
            return {
                'timestamp': time.time(),
                'error': str(e),
                'system': {},
                'processes': []
            }

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
            self.logger.debug(f"Collected CPU usage: {usage}")
            return usage
        except Exception as e:
            self.logger.error(f"Error collecting CPU usage: {e}", exc_info=True)
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
            self.logger.debug(f"Collected memory usage: {usage}")
            return usage
        except Exception as e:
            self.logger.error(f"Error collecting memory usage: {e}", exc_info=True)
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
            self.logger.debug(f"Collected disk usage: {usage}")
            return usage
        except Exception as e:
            self.logger.error(f"Error collecting disk usage: {e}", exc_info=True)
            return {"error": str(e)}

    def _get_process_details(self, proc: psutil.Process) -> Dict[str, Any]:
        """
        Gathers detailed metrics for a single process.

        Returns:
            A dictionary containing detailed metrics for the process.
        """
        try:
            # Implement the logic to gather detailed metrics for a single process
            # This is a placeholder and should be replaced with the actual implementation
            return {}
        except Exception as e:
            self.logger.error(f"Error gathering process details: {e}", exc_info=True)
            return {"error": str(e)}

