"""
Error handling utilities and retry mechanisms.

Provides standardized error responses, retry decorators, and exception handling
patterns to eliminate code duplication across the codebase.
"""

from __future__ import annotations

import asyncio
import functools
import json
import time
from collections.abc import Callable
from typing import Any, TypeVar

from .config import database_config
from .logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


# ============================================================================
# Error Response Helpers
# ============================================================================


def create_error_response(error: str, error_type: str = "error", **extra_fields) -> str:
    """
    Create a standardized error response in JSON format.

    Args:
        error: Error message
        error_type: Type of error (error, validation_error, etc.)
        **extra_fields: Additional fields to include in response

    Returns:
        JSON string with error response
    """
    response = {"success": False, "error": error, "error_type": error_type, **extra_fields}
    return json.dumps(response, indent=2)


def create_success_response(data: dict, **extra_fields) -> str:
    """
    Create a standardized success response in JSON format.

    Args:
        data: Response data
        **extra_fields: Additional fields to include in response

    Returns:
        JSON string with success response
    """
    response = {"success": True, **data, **extra_fields}
    return json.dumps(response, indent=2)


def create_validation_error(field: str, message: str, **extra_fields) -> str:
    """
    Create a validation error response.

    Args:
        field: Field that failed validation
        message: Validation error message
        **extra_fields: Additional fields

    Returns:
        JSON string with validation error
    """
    return create_error_response(
        error=message, error_type="validation_error", field=field, **extra_fields
    )


# ============================================================================
# Retry Decorators
# ============================================================================


def retry_with_backoff(
    max_retries: int = None,
    initial_delay: float = None,
    backoff_factor: float = None,
    exceptions: tuple = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function(attempt, exception) called on each retry

    Usage:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        def my_function():
            # ... code that might fail

    Returns:
        Decorated function
    """
    # Use config defaults if not specified
    max_retries = max_retries or database_config.MAX_DB_RETRIES
    initial_delay = initial_delay or database_config.INITIAL_RETRY_DELAY
    backoff_factor = backoff_factor or database_config.RETRY_BACKOFF_FACTOR

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                        )

                        # Call retry callback if provided
                        if on_retry:
                            on_retry(attempt + 1, e)

                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"Failed after {max_retries} attempts in {func.__name__}: {e}")

            # If we get here, all retries failed
            raise last_exception

        return wrapper

    return decorator


def async_retry_with_backoff(
    max_retries: int = None,
    initial_delay: float = None,
    backoff_factor: float = None,
    exceptions: tuple = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
):
    """
    Async version of retry_with_backoff decorator.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function(attempt, exception) called on each retry

    Usage:
        @async_retry_with_backoff(max_retries=3, initial_delay=1.0)
        async def my_async_function():
            # ... async code that might fail

    Returns:
        Decorated async function
    """
    # Use config defaults if not specified
    max_retries = max_retries or database_config.MAX_DB_RETRIES
    initial_delay = initial_delay or database_config.INITIAL_RETRY_DELAY
    backoff_factor = backoff_factor or database_config.RETRY_BACKOFF_FACTOR

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Async retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                        )

                        # Call retry callback if provided
                        if on_retry:
                            on_retry(attempt + 1, e)

                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"Async failed after {max_retries} attempts in {func.__name__}: {e}"
                        )

            # If we get here, all retries failed
            raise last_exception

        return wrapper

    return decorator


# ============================================================================
# Exception Classes
# ============================================================================


class Crawl4AIError(Exception):
    """Base exception for Crawl4AI MCP errors."""

    pass


class ValidationError(Crawl4AIError):
    """Raised when input validation fails."""

    pass


class ConfigurationError(Crawl4AIError):
    """Raised when configuration is invalid or missing."""

    pass


class DatabaseError(Crawl4AIError):
    """Raised when database operations fail."""

    pass


class CrawlError(Crawl4AIError):
    """Raised when crawling operations fail."""

    pass


class EmbeddingError(Crawl4AIError):
    """Raised when embedding generation fails."""

    pass


class Neo4jError(Crawl4AIError):
    """Raised when Neo4j operations fail."""

    pass


# ============================================================================
# Context Managers
# ============================================================================


class error_handler:
    """
    Context manager for consistent error handling and logging.

    Usage:
        with error_handler("database operation", reraise=True):
            # ... code that might fail
    """

    def __init__(
        self,
        operation_name: str,
        reraise: bool = True,
        default_return: Any = None,
        logger_instance: Any | None = None,
    ):
        """
        Initialize error handler.

        Args:
            operation_name: Name of the operation for logging
            reraise: Whether to reraise the exception after logging
            default_return: Value to return if exception occurs and reraise=False
            logger_instance: Custom logger to use (uses module logger if None)
        """
        self.operation_name = operation_name
        self.reraise = reraise
        self.default_return = default_return
        self.logger = logger_instance or logger
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.exception = exc_val
            self.logger.exception(f"Error during {self.operation_name}: {exc_val}")

            if not self.reraise:
                # Suppress the exception
                return True

        return False

    def get_return_value(self):
        """Get the return value if an exception occurred."""
        if self.exception is not None:
            return self.default_return
        return None


# ============================================================================
# Validation Helpers
# ============================================================================


def validate_url(url: str) -> tuple[bool, str | None]:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL is required and cannot be empty"

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        return False, "URL must start with http:// or https://"

    return True, None


def validate_range(
    value: int | float,
    min_val: int | float | None = None,
    max_val: int | float | None = None,
    field_name: str = "value",
) -> tuple[bool, str | None]:
    """
    Validate that a value is within a specified range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        field_name: Name of the field for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    if min_val is not None and value < min_val:
        return False, f"{field_name} must be >= {min_val}"

    if max_val is not None and value > max_val:
        return False, f"{field_name} must be <= {max_val}"

    return True, None


def validate_file_path(path: str, must_exist: bool = True) -> tuple[bool, str | None]:
    """
    Validate file path.

    Args:
        path: File path to validate
        must_exist: Whether file must exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    from pathlib import Path

    if not path or not path.strip():
        return False, "File path is required"

    file_path = Path(path)

    if must_exist and not file_path.exists():
        return False, f"File not found: {path}"

    if must_exist and not file_path.is_file():
        return False, f"Path is not a file: {path}"

    return True, None
