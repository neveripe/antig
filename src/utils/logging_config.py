"""
Logging configuration for Energy Stats Processor.

Provides centralized logging setup with configurable verbosity levels.
"""
import logging
import sys


def setup_logging(verbosity: int = 0) -> None:
    """
    Configure application logging based on verbosity level.
    
    Args:
        verbosity: Log verbosity level
            0 = WARNING and above (default, quiet mode)
            1 = INFO and above (normal operation details)
            2+ = DEBUG and above (detailed debugging information)
    
    Examples:
        >>> setup_logging(0)  # Only warnings and errors
        >>> setup_logging(1)  # Info, warnings, and errors
        >>> setup_logging(2)  # Everything including debug
    """
    # Map verbosity count to log levels
    level_map = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    
    # Cap at DEBUG level for any verbosity > 2
    level = level_map.get(verbosity, logging.DEBUG)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True  # Override any existing configuration
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name, typically __name__ of the calling module
    
    Returns:
        Logger instance
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    return logging.getLogger(name)
