from pydantic import BaseModel, Field, validator
from typing import Literal, List

class LoggingConfig(BaseModel):
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
    log_file: str = "logs/agent.log"
    rotation_when: Literal['S', 'M', 'H', 'D', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'midnight'] = 'midnight'
    rotation_interval: int = Field(1, gt=0)
    rotation_backup_count: int = Field(7, ge=0)
    compress_on_rotate: bool = True

class PredictorConfig(BaseModel):
    threshold: float = Field(80.0, ge=0.0, le=100.0)
    metric: str = "cpu_percent"

class MainLoopConfig(BaseModel):
    interval_seconds: int = Field(10, gt=0)

class RemediatorConfig(BaseModel):
    exclusion_period_seconds: int = Field(300, ge=0)
    process_whitelist: List[str] = Field(default_factory=lambda: [
        "cursor", "code", "firefox", "chrome", "gnome-shell", 
        "systemd", "ssh", "bash", "python3", "docker", "containerd"
    ])
    min_memory_threshold: float = Field(5.0, ge=0.0, le=100.0)

class AppConfig(BaseModel):
    logging: LoggingConfig
    predictor: PredictorConfig
    main_loop: MainLoopConfig
    remediator: RemediatorConfig 