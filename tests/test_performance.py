import subprocess
import time
import psutil
import pytest
import os
from pathlib import Path

AGENT_MAIN_SCRIPT = "src/main.py"
PERFORMANCE_LOG = Path("logs/performance.log")

@pytest.fixture(scope="module")
def setup_performance_test():
    # Ensure log directory exists and the log file is clean
    PERFORMANCE_LOG.parent.mkdir(exist_ok=True)
    if PERFORMANCE_LOG.exists():
        PERFORMANCE_LOG.unlink()
    yield

def test_agent_performance(setup_performance_test):
    """
    Measures the CPU and Memory usage of the agent process over a short duration.
    """
    agent_process = None
    try:
        # Start the agent
        agent_process = subprocess.Popen(
            ["python3", AGENT_MAIN_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Started agent with PID: {agent_process.pid}")

        # Wait for the agent to initialize
        time.sleep(5)

        # Get the psutil Process object
        try:
            p = psutil.Process(agent_process.pid)
        except psutil.NoSuchProcess:
            pytest.fail(f"Agent process with PID {agent_process.pid} disappeared unexpectedly.")

        # Monitor for a short duration
        monitoring_duration = 30  # seconds
        end_time = time.time() + monitoring_duration
        
        cpu_readings = []
        memory_readings = []

        print("Starting performance monitoring...")
        with open(PERFORMANCE_LOG, 'a') as f:
            f.write("timestamp,cpu_percent,memory_mb\\n")
            while time.time() < end_time:
                try:
                    with p.oneshot():
                        cpu_percent = p.cpu_percent(interval=1.0)
                        memory_info = p.memory_info()
                        memory_mb = memory_info.rss / (1024 * 1024) # Resident Set Size in MB

                        cpu_readings.append(cpu_percent)
                        memory_readings.append(memory_mb)

                        log_entry = f"{time.time()},{cpu_percent},{memory_mb}\\n"
                        f.write(log_entry)
                        print(f"Logged: CPU={cpu_percent}%, Memory={memory_mb:.2f} MB")

                except psutil.NoSuchProcess:
                    print("Agent process terminated during monitoring.")
                    break
                time.sleep(4) # Interval between readings

        print("Performance monitoring finished.")

        # Basic assertions on the collected data
        assert len(cpu_readings) > 0, "No CPU readings were collected."
        assert len(memory_readings) > 0, "No memory readings were collected."

        avg_cpu = sum(cpu_readings) / len(cpu_readings)
        avg_mem = sum(memory_readings) / len(memory_readings)
        max_mem = max(memory_readings)

        print(f"Average CPU Usage: {avg_cpu:.2f}%")
        print(f"Average Memory Usage: {avg_mem:.2f} MB")
        print(f"Maximum Memory Usage: {max_mem:.2f} MB")

        # Define acceptable performance thresholds (these are examples)
        MAX_AVG_CPU_THRESHOLD = 20.0 # %
        MAX_MEM_THRESHOLD_MB = 100.0 # MB

        assert avg_cpu < MAX_AVG_CPU_THRESHOLD, f"Average CPU usage ({avg_cpu:.2f}%) exceeded threshold ({MAX_AVG_CPU_THRESHOLD}%)"
        assert max_mem < MAX_MEM_THRESHOLD_MB, f"Maximum memory usage ({max_mem:.2f} MB) exceeded threshold ({MAX_MEM_THRESHOLD_MB} MB)"

    finally:
        # Cleanup
        if agent_process and agent_process.poll() is None:
            agent_process.terminate()
            agent_process.wait()
            print("Agent process terminated.") 