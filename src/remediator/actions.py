import psutil
from src.logger import setup_logger

log = setup_logger(__name__)

def kill_process_by_pid(pid: int) -> bool:
    """
    Terminates a process with the given PID.

    Args:
        pid (int): The process ID to terminate.

    Returns:
        bool: True if the process was terminated successfully, False otherwise.
    """
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        
        log.warning(f"Attempting to terminate process '{proc_name}' (PID: {pid})...")
        proc.terminate()  # Sends SIGTERM, a graceful shutdown signal
        
        # Wait for the process to terminate
        try:
            proc.wait(timeout=3)
            log.info(f"Process '{proc_name}' (PID: {pid}) terminated successfully.")
            return True
        except psutil.TimeoutExpired:
            log.warning(f"Process '{proc_name}' (PID: {pid}) did not terminate gracefully. Forcing kill.")
            proc.kill()  # Sends SIGKILL
            proc.wait(timeout=3)
            log.info(f"Process '{proc_name}' (PID: {pid}) killed successfully.")
            return True

    except psutil.NoSuchProcess:
        log.error(f"Failed to kill process: No process with PID {pid} found.")
        return False
    except psutil.AccessDenied:
        log.error(f"Failed to kill process {pid}: Access Denied. Agent may lack necessary permissions.")
        return False
    except Exception as e:
        log.error(f"An unexpected error occurred while trying to kill process {pid}: {e}", exc_info=True)
        return False
