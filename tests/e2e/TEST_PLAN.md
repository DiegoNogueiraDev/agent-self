# End-to-End Test Plan

This document outlines the test scenarios for validating the end-to-end functionality of the Self-Healing Agent.

## Scenarios

### 1. Normal Operation
- **Description:** The agent runs, collects system metrics, but no anomalies are detected as no process exceeds the defined threshold.
- **Expected Outcome:**
    - The agent logs regular metric collection snapshots.
    - No remediation actions are triggered.
    - The application runs indefinitely without errors.

### 2. Anomaly Detection and Successful Remediation
- **Description:** A dummy process is started that intentionally consumes memory above the configured threshold. The agent should detect this anomaly and perform remediation.
- **Expected Outcome:**
    - The agent identifies the high-consumption process as an offender.
    - The agent triggers the `kill_process_by_pid` action.
    - A structured JSON log message is recorded for the remediation action, with `"success": true`.
    - The dummy process is terminated.

### 3. Remediation Failure (Process Not Found)
- **Description:** The agent identifies an offender, but the process terminates on its own before the agent can kill it.
- **Expected Outcome:**
    - The agent attempts to kill the process.
    - The `kill_process_by_pid` action fails because the PID no longer exists.
    - A structured JSON log message is recorded with `"success": false`.

### 4. Process Exclusion
- **Description:** A process that was recently actioned upon (and failed to be terminated, hypothetically) should be temporarily excluded from further remediation attempts to prevent action loops.
- **Expected Outcome:**
    - After a failed remediation attempt on a PID, the agent adds the PID to an exclusion list.
    - In the next cycle, even if the process is still identified as an offender, no remediation action is taken for that specific PID.
    - A log message indicates that the process is on the exclusion list. 