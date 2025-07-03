from typing import List, Dict, Any, Optional
from src.logger import setup_logger
from .actions import kill_process_by_pid
import time
import json

log = setup_logger(__name__)

class Remediator:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.action_history = []
        self.exclusion_list = {} # Temporarily exclude PIDs from being actioned on
        self.exclusion_period_seconds = self.config.get("exclusion_period_seconds", 300)

    def _analyze_root_cause(self, snapshot: List[Dict[str, Any]], top_n: int = 1) -> List[Dict[str, Any]]:
        """
        Analyzes a snapshot of process metrics to find the top N processes
        consuming the most memory.
        """
        if not snapshot:
            return []
        try:
            # Exclude PIDs on the temporary exclusion list
            valid_processes = [
                p for p in snapshot 
                if isinstance(p, dict) and p.get('pid') not in self.exclusion_list
            ]
            sorted_processes = sorted(
                valid_processes, 
                key=lambda p: p.get('memory_percent', 0), 
                reverse=True
            )
            return sorted_processes[:top_n]
        except (TypeError, KeyError) as e:
            log.error(f"Error during root cause analysis: {e}", exc_info=True)
            return []

    def perform_remediation(self, snapshot: Dict[str, Any]):
        """
        Performs remediation and includes a basic rollback/safety mechanism.
        """
        log.info("Performing remediation...")
        top_offenders = self._analyze_root_cause(snapshot.get('processes', []))

        if not top_offenders:
            log.info("RCA did not identify specific offending processes. No action taken.")
            return

        for offender in top_offenders:
            pid = offender.get('pid')
            if pid:
                log.warning(f"Top memory offender identified: {offender.get('name')} (PID: {pid}). Taking action.")
                
                success = kill_process_by_pid(pid)
                
                action_record = {
                    'action': 'kill_process_by_pid',
                    'pid': pid,
                    'offender_details': offender,
                    'snapshot_context': snapshot,
                    'success': success,
                    'timestamp': time.time()
                }
                
                # Log the entire action record as a JSON string
                log.info(json.dumps(action_record))
                
                self.action_history.append(action_record)

                # ALWAYS add to exclusion list after an action is taken.
                # The verification step will determine if the anomaly is truly gone.
                # This prevents repeat actions on the same PID during verification.
                log.info(f"Adding PID {pid} to exclusion list for {self.exclusion_period_seconds} seconds to prevent remediation loops.")
                self.exclusion_list[pid] = time.time() + self.exclusion_period_seconds

                if not success:
                    log.error(f"Remediation action failed for PID {pid}.")
            else:
                log.error("Analysis identified an offender, but it has no PID.")
        
        # Clean up old entries from the exclusion list
        self._cleanup_exclusion_list()

    def _cleanup_exclusion_list(self):
        current_time = time.time()
        expired_pids = [pid for pid, expiry in self.exclusion_list.items() if current_time > expiry]
        for pid in expired_pids:
            del self.exclusion_list[pid]
            log.info(f"Removed PID {pid} from remediation exclusion list.")

# For backwards compatibility, we can keep the standalone function for now,
# but new logic should use the Remediator class.
def analyze_root_cause(snapshot: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    return Remediator()._analyze_root_cause(snapshot, top_n)
