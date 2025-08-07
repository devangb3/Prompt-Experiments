"""
Logging configuration for AI Prompt Sender
Supports configurable log levels via environment variables
"""

import logging
import os
import sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOG_LEVEL = "INFO"

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

def get_log_level() -> int:
    """Get log level from environment variable"""
    log_level_str = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    return LOG_LEVELS.get(log_level_str, LOG_LEVELS[DEFAULT_LOG_LEVEL])

def get_log_file() -> Optional[str]:
    """Get log file path from environment variable"""
    return os.getenv("LOG_FILE")

def setup_logging(
    name: str = "ai_prompt_sender",
    log_level: Optional[int] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        name: Logger name
        log_level: Log level (if None, will use environment variable)
        log_format: Log message format
        log_file: Optional log file path (if None, will use environment variable)
    
    Returns:
        Configured logger instance
    """
    if log_level is None:
        log_level = get_log_level()
    
    if log_file is None:
        log_file = get_log_file()
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    logger.handlers.clear()
    
    formatter = logging.Formatter(log_format)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        try:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to setup file logging to {log_file}: {e}")
    
    logger.propagate = False
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (if None, uses 'ai_prompt_sender')
    
    Returns:
        Logger instance
    """
    if name is None:
        name = "ai_prompt_sender"
    
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        setup_logging(name)
    
    return logger

default_logger = get_logger() 