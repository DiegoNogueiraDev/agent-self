import subprocess
import time
import pytest
import os
import signal
import json
from pathlib import Path

# Path to the agent's main script
AGENT_MAIN_SCRIPT = "src/main.py"
LOG_FILE = Path("logs/agent.log")
CONFIG_FILE = "config/config.yaml"

# A simple python script that allocates memory to act as the offender
OFFENDER_SCRIPT_CONTENT = """
import time
import sys

# Allocate a large chunk of memory (e.g., 500 MB)
try:
    memory_hog = ' ' * (500 * 1024 * 1024)
    print(f"Offender process (PID: {os.getpid()}) started and allocated memory.")
except MemoryError:
    print("Failed to allocate memory.")
    sys.exit(1)

# Keep the process alive
while True:
    time.sleep(1)
"""

@pytest.fixture(scope="module")
def setup_e2e_env():
    # Ensure log directory exists and the log file is clean
    LOG_FILE.parent.mkdir(exist_ok=True)
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    # Create the offender script file
    offender_script_path = Path("tests/e2e/offender.py")
    offender_script_path.write_text(OFFENDER_SCRIPT_CONTENT)

    # Modify the agent's config for faster testing
    # (e.g., shorter interval)
    # For now, we'll use the default config

    yield offender_script_path

    # Teardown: remove offender script
    if offender_script_path.exists():
        offender_script_path.unlink()

def start_process(command):
    # Use Popen to start a non-blocking process
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def test_anomaly_detection_and_remediation(setup_e2e_env):
    offender_script = setup_e2e_env
    agent_process = None
    offender_process = None

    try:
        # Start the offender process
        offender_process = start_process(["python3", str(offender_script)])
        time.sleep(2) # Give it time to start and allocate memory
        offender_pid = offender_process.pid
        print(f"Started offender with PID: {offender_pid}")

        # Start the agent
        agent_process = start_process(["python3", AGENT_MAIN_SCRIPT])
        print(f"Started agent with PID: {agent_process.pid}")

        # Monitor the log file for the remediation action
        remediation_logged = False
        start_time = time.time()
        timeout = 90 # seconds

        while time.time() - start_time < timeout:
            if not LOG_FILE.exists():
                time.sleep(1)
                continue

            with open(LOG_FILE, 'r') as f:
                for line in f:
                    try:
                        # Find the start of the JSON object
                        json_start_index = line.find('{')
                        if json_start_index == -1:
                            continue
                        
                        log_json_str = line[json_start_index:]
                        log_data = json.loads(log_json_str)

                        # Check if this is the remediation log we are looking for
                        if (log_data.get('action') == 'kill_process_by_pid' and 
                            log_data.get('pid') == offender_pid):
                            
                            print(f"Found remediation log for PID {offender_pid}: {log_json_str.strip()}")
                            assert log_data.get('success') is True, "Remediation was logged as unsuccessful."
                            remediation_logged = True
                            break

                    except (json.JSONDecodeError, KeyError):
                        # Ignore lines that are not valid JSON or don't have the expected keys
                        continue
            
            if remediation_logged:
                break
            
            print("...waiting for remediation log...")
            time.sleep(2)

        assert remediation_logged, "Remediation action was not logged within the timeout."

        # Verify that the offender process was actually killed
        time.sleep(2) # Give time for the process to terminate
        poll_result = offender_process.poll()
        assert poll_result is not None, "Offender process was not terminated."

    finally:
        # Cleanup
        print("Cleaning up processes...")
        if agent_process and agent_process.poll() is None:
            agent_process.terminate()
            agent_process.wait()
            print("Agent process terminated.")
        if offender_process and offender_process.poll() is None:
            offender_process.terminate()
            offender_process.wait()
            print("Offender process terminated.") 