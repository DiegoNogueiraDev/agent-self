import logging
import sys
import gzip
import shutil
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from src.config import get_config


class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Extended version of TimedRotatingFileHandler that compresses logs on rollover.
    """
    def doRollover(self):
        """
        Do a rollover, compressing the old log file.
        """
        super().doRollover()
        
        # After the standard rollover, compress the rolled-over file
        log_file_path = Path(self.baseFilename)
        rotated_log_path_str = self.baseFilename + "." + self.suffix
        rotated_log_path = Path(rotated_log_path_str)

        if rotated_log_path.exists():
            compressed_log_path = Path(f"{rotated_log_path_str}.gz")
            with open(rotated_log_path, 'rb') as f_in:
                with gzip.open(compressed_log_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove the uncompressed log file
            rotated_log_path.unlink()


def setup_logger(name: str, level=None):
    """
    Sets up a logger with a configurable timed rotating file handler.
    
    Args:
        name (str): The name of the logger.
        level: The logging level. If None, it's taken from config.
        
    Returns:
        A configured logger instance.
    """
    config = get_config().get("logging", {})

    log_level_str = config.get("level", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Allow overriding the config level
    if level is not None:
        log_level = level

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File Handler
    log_file_path_str = config.get("log_file", "agent.log")
    log_file_path = Path(log_file_path_str)
    
    # Ensure the directory for the log file exists
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    when = config.get("rotation_when", "midnight")
    interval = config.get("rotation_interval", 1)
    backup_count = config.get("rotation_backup_count", 7)
    compress = config.get("compress_on_rotate", False)

    handler_class = CompressedTimedRotatingFileHandler if compress else TimedRotatingFileHandler

    file_handler = handler_class(
        log_file_path, 
        when=when, 
        interval=interval, 
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Example of a default logger
log = setup_logger(__name__)
