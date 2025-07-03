from pydantic import BaseModel, Field, validator
from typing import Literal

class LoggingConfig(BaseModel):
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
    log_file: str = "logs/agent.log"
    rotation_when: Literal['S', 'M', 'H', 'D', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'midnight'] = 'midnight'
    rotation_interval: int = Field(1, gt=0)
    rotation_backup_count: int = Field(7, ge=0)
    compress_on_rotate: bool = True

class PredictorConfig(BaseModel):
    threshold: float = Field(0.8, ge=0.0, le=1.0)
    metric: str = "memory_percent"

class MainLoopConfig(BaseModel):
    interval_seconds: int = Field(60, gt=0)

class RemediatorConfig(BaseModel):
    exclusion_period_seconds: int = Field(300, ge=0)

class AppConfig(BaseModel):
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    predictor: PredictorConfig = Field(default_factory=PredictorConfig)
    main_loop: MainLoopConfig = Field(default_factory=MainLoopConfig)
    remediator: RemediatorConfig = Field(default_factory=RemediatorConfig) 