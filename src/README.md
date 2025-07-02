# Source Code (`src`)

This directory contains the core source code for the Self-Healing AI Agent. The project is organized into a modular structure to ensure separation of concerns and maintainability.

## Modules

Below is an overview of the main modules and their responsibilities:

### 1. `collector`
*   **Responsibility:** Gathers time-series data from the host machine.
*   **Key Components:**
    *   `collector.py`: Contains the main logic for collecting metrics like CPU, memory, and disk usage at regular intervals. It uses the `psutil` library.

### 2. `predictor`
*   **Responsibility:** Analyzes the collected data to predict potential system issues.
*   **Key Components:**
    *   `predictor.py`: Loads a pre-trained AI model and uses it to perform inference on the incoming data stream from the collector.
    *   `models/`: This directory stores the trained model files (e.g., in `.onnx` or a similar format).

### 3. `remediator`
*   **Responsibility:** Executes corrective actions based on the predictions from the predictor module.
*   **Key Components:**
    *   `remediator.py`: Orchestrates the remediation process. It decides which action to take based on the type of predicted issue.
    *   `actions.py`: Contains a library of specific remediation functions (e.g., `restart_process`, `clear_cache`).

### 4. `logger`
*   **Responsibility:** Manages all logging activities for the agent.
*   **Key Components:**
    *   `logger.py`: Provides a centralized and configurable logging setup for the entire application, ensuring that all events, predictions, and actions are recorded.

### 5. `main.py`
*   **Responsibility:** The main entry point of the application. It initializes and orchestrates all the other modules, creating the main application loop.

## Other Directories

*   **`config/`**: Contains configuration files, such as `config.yaml`, for setting up agent parameters.
*   **`tests/`**: Contains unit and integration tests for all modules.
*   **`scripts/`**: Holds utility scripts, such as `train_model.py` for training the AI model. 