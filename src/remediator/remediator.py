from typing import List, Dict, Any, Optional
from src.logger import setup_logger
from .actions import kill_processes_by_pids
import time
import json
import psutil

log = setup_logger(__name__)

class Remediator:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.action_history = []
        self.exclusion_list = {} # Temporarily exclude PIDs from being actioned on
        self.exclusion_period_seconds = self.config.get("exclusion_period_seconds", 300)
        self.process_whitelist = self.config.get("process_whitelist", [])
        if self.process_whitelist:
            log.info(f"Remediator initialized with a whitelist of {len(self.process_whitelist)} processes.")

    def _analyze_root_cause(self, snapshot: List[Dict[str, Any]], metric: str, top_n: int = 1) -> List[Dict[str, Any]]:
        """
        Analyzes a snapshot of process metrics to find the top N processes
        based on a specific metric (e.g., 'cpu_percent' or 'memory_percent').
        """
        if not snapshot:
            return []
        try:
            # Exclude PIDs on the temporary exclusion list and processes on the permanent whitelist
            valid_processes = [
                p for p in snapshot 
                if (isinstance(p, dict) and 
                    p.get('pid') not in self.exclusion_list and
                    p.get('name') not in self.process_whitelist)
            ]
            sorted_processes = sorted(
                valid_processes, 
                key=lambda p: p.get(metric, 0), 
                reverse=True
            )
            return sorted_processes[:top_n]
        except (TypeError, KeyError) as e:
            log.error(f"Error during root cause analysis for metric '{metric}': {e}", exc_info=True)
            return []

    def perform_remediation(self, prediction: Dict[str, Any], snapshot: Dict[str, Any]):
        """
        Performs remediation based on the detected anomaly type from the prediction
        and the process list from the snapshot.
        """
        log.info("Performing remediation...")
        
        metric_to_check = prediction.get('anomaly_type')

        if not metric_to_check:
            log.warning(f"No remediation metric defined for anomaly type '{prediction.get('anomaly_type')}'. No action taken.")
            return

        # Get the list of processes from the overall system snapshot
        processes = snapshot.get('processes', [])
        top_offenders = self._analyze_root_cause(processes, metric=metric_to_check)

        if not top_offenders:
            log.info("RCA did not identify specific offending processes. No action taken.")
            return

        for offender in top_offenders:
            pids_to_kill = []
            try:
                main_offender_proc = psutil.Process(offender.get('pid'))
                parent = main_offender_proc.parent()
                # Ensure parent process exists before trying to access its properties
                if parent:
                    pids_to_kill = [child.pid for child in parent.children(recursive=False)]
                    log.warning(
                        f"Group remediation triggered by PID {main_offender_proc.pid} "
                        f"({main_offender_proc.name()}). Targeting {len(pids_to_kill)} "
                        f"sibling processes under parent PID {parent.pid} ({parent.name()})."
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError) as e:
                log.warning(f"Could not determine process group due to error: {e}. Falling back to single-process kill.")
                # Fallback to single-process kill if parent/children cannot be determined
                
            # If group logic failed or wasn't applicable, ensure we target the main offender
            if not pids_to_kill and offender.get('pid'):
                 pids_to_kill = [offender.get('pid')]
                 log.warning(
                     f"Targeting single offender '{offender.get('name')}' (PID: {offender.get('pid')}) "
                     f"with {metric_to_check}: {offender.get(metric_to_check, 'N/A')}%."
                 )

            # Filter out any None values from the list to ensure type safety
            pids_to_kill_filtered = [pid for pid in pids_to_kill if pid is not None]

            if not pids_to_kill_filtered:
                log.error("Analysis identified an offender, but could not resolve a valid PID to kill.")
                continue

            # Ação de remediação para o grupo
            success = kill_processes_by_pids(pids_to_kill_filtered) # Use the new function
            
            action_record = {
                'action': 'kill_process_group_by_pid',
                'pids': pids_to_kill_filtered,
                'triggering_offender': offender,
                'snapshot_context': prediction,
                'success': success,
                'timestamp': time.time()
            }
            log.info(json.dumps(action_record))
            self.action_history.append(action_record)

            for pid in pids_to_kill_filtered:
                self.exclusion_list[pid] = time.time() + self.exclusion_period_seconds
            
            log.info(f"Added {len(pids_to_kill_filtered)} PIDs to exclusion list.")
            if not success:
                log.error(f"Group remediation action failed for PIDs: {pids_to_kill_filtered}")
        
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
    # This standalone function is now ambiguous. It's better to deprecate it,
    # but for now, we'll leave it defaulting to memory as it was before.
    return Remediator()._analyze_root_cause(snapshot, metric='memory_percent', top_n=top_n)
