import psutil
from src.logger import setup_logger
from typing import List

log = setup_logger(__name__)

def kill_processes_by_pids(pids: List[int]) -> bool:
    """
    Terminates a list of processes given their PIDs.

    Args:
        pids (List[int]): A list of process IDs to terminate.

    Returns:
        bool: True if all processes were terminated successfully, False otherwise.
    """
    all_success = True
    procs_to_wait = []

    for pid in pids:
        try:
            proc = psutil.Process(pid)
            procs_to_wait.append(proc)
            log.warning(f"Sending terminate signal to process '{proc.name()}' (PID: {pid})...")
            proc.terminate()
        except psutil.NoSuchProcess:
            log.warning(f"Process with PID {pid} not found, likely already terminated.")
            continue
        except psutil.AccessDenied:
            log.error(f"Failed to terminate process {pid}: Access Denied.")
            all_success = False
            continue
    
    if not procs_to_wait:
        return all_success

    # Wait for all gracefully terminating processes
    gone, alive = psutil.wait_procs(procs_to_wait, timeout=3)

    # Force kill any remaining processes
    for proc in alive:
        log.warning(f"Process '{proc.name()}' (PID: {proc.pid}) did not terminate gracefully. Forcing kill.")
        try:
            proc.kill()
        except psutil.AccessDenied:
            log.error(f"Failed to force kill process {proc.pid}: Access Denied.")
            all_success = False
        except psutil.NoSuchProcess:
            # Already gone, which is a success in this context
            pass

    # Final check
    gone, alive = psutil.wait_procs(alive, timeout=3)
    if alive:
        for proc in alive:
            log.error(f"Failed to kill process '{proc.name()}' (PID: {proc.pid}) even with force.")
        all_success = False

    return all_success
