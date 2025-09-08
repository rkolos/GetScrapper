"""Logging configuration for GetScrapper."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "getscrapper",
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up logger for GetScrapper.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    try:
        logger.setLevel(getattr(logging, level.upper()))
    except AttributeError:
        logger.setLevel(logging.INFO)  # Default to INFO for invalid levels
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger