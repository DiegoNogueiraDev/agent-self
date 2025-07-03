# Self-Healing AI Agent

An AI-powered agent for autonomous machine monitoring, prediction, and self-remediation. This agent monitors system metrics, predicts anomalies based on predefined thresholds, and takes automated actions to resolve them.

## Features

- **System Monitoring:** Collects key system metrics like CPU usage, memory usage, and disk I/O.
- **Anomaly Prediction:** Uses a simple threshold-based predictor to identify potential issues.
- **Self-Remediation:** Automatically takes action, such as killing high-resource processes.
- **Structured Logging:** Records all actions in a structured JSON format for easy analysis.
- **Configurable:** All key parameters can be configured via a `config.yaml` file.
- **Dockerized:** Runs in a secure, non-root container.

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` for package management
- Docker (for running in a container)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/DiegoNogueiraDev/agent-self.git
    cd agent-self
    ```

2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

The agent's behavior is controlled by the `config/config.yaml` file. You can adjust parameters such as the monitoring interval, logging settings, and remediation thresholds.

```yaml
# Example config.yaml
logging:
  level: INFO
  log_file: "logs/agent.log"
  # ... other logging settings

predictor:
  threshold: 0.80 # 80%
  metric: "memory_percent"

main_loop:
  interval_seconds: 60

remediator:
  exclusion_period_seconds: 300
```

### Usage

To run the agent directly on your machine:

```bash
python3 src/main.py
```

The agent will start monitoring your system based on the settings in `config.yaml`.

## Running with Docker

For a more isolated and secure environment, you can build and run the agent using Docker.

1.  **Build the Docker image:**
    ```bash
    docker build -t self-healing-agent .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -d --name agent --rm self-healing-agent
    ```
    - `-d`: Run in detached mode.
    - `--name agent`: Assign a name to the container.
    - `--rm`: Automatically remove the container when it exits.

To view the logs from the container:
```bash
docker logs -f agent
```
