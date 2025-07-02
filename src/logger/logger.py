import logging
import sys
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name: str, log_file: str = 'agent.log', level=logging.INFO):
    """
    Sets up a logger with a timed rotating file handler.
    
    Args:
        name (str): The name of the logger.
        log_file (str): The path to the log file.
        level: The logging level.
        
    Returns:
        A configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent the logger from propagating to the root logger
    logger.propagate = False

    # Avoid adding handlers if they already exist
    if logger.hasHandlers():
        return logger

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a handler for console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    # Create a timed rotating file handler
    # Rotates every midnight, keeps 7 days of logs
    file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7)
    file_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    return logger

# Example of a default logger
log = setup_logger(__name__)
