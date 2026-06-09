"""
Logging configuration for the Crawl4AI MCP Server.

Provides standardized logging setup with both console and file handlers,
proper formatting, and easy-to-use logger creation.
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from .config import logging_config

# Type variables for decorators
F = TypeVar("F", bound=Callable[..., Any])


def setup_logging(
    name: str = "crawl4ai_mcp",
    level: str | None = None,
    log_to_file: bool = True,
    log_dir: str | None = None,
) -> logging.Logger:
    """
    Set up logging with console and optional file handlers.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_dir: Directory for log files (uses config default if None)

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)

    # Set level
    log_level = level or logging_config.DEFAULT_LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(fmt=logging_config.LOG_FORMAT, datefmt=logging_config.DATE_FORMAT)

    # Console handler - use stderr for stdio protocol compatibility
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        log_directory = Path(log_dir or logging_config.LOG_DIR)
        log_directory.mkdir(parents=True, exist_ok=True)

        log_file = log_directory / logging_config.LOG_FILE

        # Use rotating file handler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=logging_config.MAX_LOG_SIZE,
            backupCount=logging_config.BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    If the logger doesn't exist, creates one with default configuration.

    Args:
        name: Logger name (usually __name__ from calling module)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logging(name)

    return logger


def log_function_call(func: F) -> F:
    """
    Decorator to log function calls with arguments and results.

    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return result
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.exception(f"{func.__name__} raised exception: {e}")
            raise

    return wrapper  # type: ignore


def log_async_function_call(func: F) -> F:
    """
    Decorator to log async function calls with arguments and results.

    Usage:
        @log_async_function_call
        async def my_async_function(arg1, arg2):
            return result
    """
    import functools

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        logger.debug(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Async {func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.exception(f"Async {func.__name__} raised exception: {e}")
            raise

    return wrapper  # type: ignore


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.

    Usage:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.info("Doing something")
    """

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__module__)
        return self._logger


# Create default logger for the module
default_logger = setup_logging()


# Convenience functions for quick logging
def debug(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log debug message."""
    default_logger.debug(msg, *args, **kwargs)


def info(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log info message."""
    default_logger.info(msg, *args, **kwargs)


def warning(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log warning message."""
    default_logger.warning(msg, *args, **kwargs)


def error(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log error message."""
    default_logger.error(msg, *args, **kwargs)


def critical(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log critical message."""
    default_logger.critical(msg, *args, **kwargs)


def exception(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log exception with traceback."""
    default_logger.exception(msg, *args, **kwargs)
