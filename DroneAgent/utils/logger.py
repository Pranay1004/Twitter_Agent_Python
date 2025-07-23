"""
Enhanced Logger Utility
Provides a centralized, configurable logger for the DroneAgent application.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name: str, level: int = logging.INFO):
    """
    Set up a logger with console and file handlers.

    Args:
        name (str): The name of the logger, usually __name__.
        level (int): The minimum logging level.

    Returns:
        logging.Logger: A configured logger instance.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "drone_agent.log"

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def log_api_usage(api_name: str):
    """Log the usage of an API."""
    usage_logger = setup_logger("api_usage")
    usage_logger.info(f"API Used: {api_name}")

def log_thread_post(thread_data: dict):
    """Log the details of a posted thread."""
    post_logger = setup_logger("thread_poster")
    summary = {
        "theme": thread_data.get("theme"),
        "total_tweets": thread_data.get("total_tweets"),
        "generated_at": thread_data.get("generated_at"),
    }
    post_logger.info(f"Thread posted: {summary}")

    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_thread_post(thread_data: dict, success: bool):
    """Log thread posting attempt"""
    logger = setup_logger("poster")
    
    if success:
        logger.info(f"✅ Posted thread: {thread_data.get('topic', 'Unknown')} "
                   f"({len(thread_data.get('tweets', []))} tweets)")
    else:
        logger.error(f"❌ Failed to post thread: {thread_data.get('topic', 'Unknown')}")

def log_api_usage(api_name: str, endpoint: str, success: bool, response_time: float = None):
    """Log API usage statistics"""
    logger = setup_logger("api")
    
    status = "✅" if success else "❌"
    message = f"{status} {api_name} - {endpoint}"
    
    if response_time:
        message += f" ({response_time:.2f}s)"
        
    if success:
        logger.info(message)
    else:
        logger.warning(message)
