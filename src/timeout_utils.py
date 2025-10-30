"""
Timeout utilities for external API calls and long-running operations.

Provides timeout protection for:
- Azure OpenAI API calls
- Database operations (Supabase, Neo4j)
- Web crawling operations
"""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable
from typing import TypeVar

from .config import crawl_config

T = TypeVar("T")


async def with_timeout(
    coro: Callable[..., T], timeout: float, operation_name: str = "Operation"
) -> T:
    """
    Execute an async operation with timeout protection.

    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds
        operation_name: Name of operation for error messages

    Returns:
        Result of the coroutine

    Raises:
        TimeoutError: If operation exceeds timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(
            f"{operation_name} timed out after {timeout} seconds. "
            f"Consider increasing timeout or checking service availability."
        )


def timeout_wrapper(timeout_seconds: float = None, operation_name: str = None):
    """
    Decorator to add timeout protection to async functions.

    Usage:
        @timeout_wrapper(timeout_seconds=30, operation_name="API call")
        async def my_api_call():
            ...

    Args:
        timeout_seconds: Timeout in seconds (uses default if None)
        operation_name: Name for error messages (uses function name if None)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            timeout = timeout_seconds or crawl_config.DEFAULT_TIMEOUT
            op_name = operation_name or func.__name__

            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(f"{op_name} timed out after {timeout} seconds")

        return wrapper

    return decorator


class TimeoutManager:
    """
    Context manager for timeout protection.

    Usage:
        async with TimeoutManager(30, "Database query") as tm:
            result = await long_operation()
    """

    def __init__(self, timeout: float, operation_name: str = "Operation"):
        self.timeout = timeout
        self.operation_name = operation_name
        self._task = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # If timeout occurred, exc_type will be TimeoutError
        if exc_type is asyncio.TimeoutError:
            raise TimeoutError(f"{self.operation_name} timed out after {self.timeout} seconds")
        return False


# Pre-configured timeout wrappers for common operations
def api_timeout(func: Callable) -> Callable:
    """Timeout wrapper for API calls (30s default)."""
    return timeout_wrapper(
        timeout_seconds=crawl_config.API_TIMEOUT, operation_name=f"API call: {func.__name__}"
    )(func)


def database_timeout(func: Callable) -> Callable:
    """Timeout wrapper for database operations (60s default)."""
    return timeout_wrapper(
        timeout_seconds=crawl_config.DATABASE_TIMEOUT,
        operation_name=f"Database operation: {func.__name__}",
    )(func)


def crawler_timeout(func: Callable) -> Callable:
    """Timeout wrapper for crawling operations (120s default)."""
    return timeout_wrapper(
        timeout_seconds=crawl_config.CRAWLER_TIMEOUT,
        operation_name=f"Crawler operation: {func.__name__}",
    )(func)
