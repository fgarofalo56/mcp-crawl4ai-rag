"""
Stdout safety module for MCP server.

This module ensures that NO output goes to stdout except valid JSON-RPC messages.
All library logging, debug output, and print statements are redirected to stderr.

This is critical for MCP servers using stdio transport, as stdout contamination
causes JSON parsing errors in Claude Desktop.

Bug Fix: Addresses "[FETCH]" and other non-JSON output appearing in stdout,
causing "Unexpected token" JSON parsing errors.
"""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from typing import Any


class StderrRedirector:
    """
    Redirects stdout to stderr to prevent MCP protocol contamination.

    This ensures that any library that writes to stdout (httpx, requests,
    Crawl4AI, etc.) will have their output redirected to stderr instead.
    """

    def __init__(self) -> None:
        self.original_stdout: Any = sys.stdout
        self.stderr: Any = sys.stderr

    def __enter__(self) -> StderrRedirector:
        """Redirect stdout to stderr."""
        sys.stdout = self.stderr
        return self

    def __exit__(
        self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any | None
    ) -> bool:
        """Restore original stdout."""
        sys.stdout = self.original_stdout
        return False


@contextmanager
def suppress_stdout() -> Iterator[None]:
    """
    Context manager to temporarily suppress stdout output.

    Use this when calling library functions that might print to stdout.

    Example:
        with suppress_stdout():
            some_library_function()  # Any stdout output is discarded
    """
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout


def configure_logging_for_mcp() -> None:
    """
    Configure Python logging to ONLY use stderr.

    This ensures that all logging output goes to stderr, never stdout.
    Also configures third-party library loggers to use stderr.
    """
    # Configure root logger to use stderr
    root_logger = logging.getLogger()
    root_logger.handlers = []  # Remove any existing handlers

    # Create stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    root_logger.addHandler(stderr_handler)
    root_logger.setLevel(logging.WARNING)

    # Configure third-party loggers to use stderr and reduce verbosity
    third_party_loggers = [
        "httpx",
        "httpcore",
        "requests",
        "urllib3",
        "crawl4ai",
        "playwright",
        "asyncio",
        "supabase",
        "postgrest",
        "neo4j",
        "openai",
        "anthropic",
    ]

    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(stderr_handler)
        logger.setLevel(logging.ERROR)  # Only show errors
        logger.propagate = False  # Don't propagate to root logger


def setup_mcp_stdout_safety() -> None:
    """
    Main setup function to ensure stdout safety for MCP server.

    Call this at the very beginning of your MCP server startup,
    before any other imports or operations.

    This function:
    1. Configures logging to use stderr only
    2. Sets environment variables to suppress library output
    3. Warns if stdout has been contaminated
    """
    # Configure logging first
    configure_logging_for_mcp()

    # Set environment variables to suppress verbose library output
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUNBUFFERED"] = "1"  # Ensure immediate stderr output

    # Suppress httpx logging (major source of [FETCH] messages)
    os.environ["HTTPX_LOG_LEVEL"] = "ERROR"

    # Suppress Playwright logging
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
    os.environ["DEBUG"] = ""  # Disable debug mode

    # Verify stdout is clean (hasn't been written to yet)
    if hasattr(sys.stdout, "getvalue"):
        # stdout has been replaced with StringIO, check if it has content
        content = sys.stdout.getvalue()
        if content.strip():
            print(
                f"⚠️  WARNING: stdout contamination detected ({len(content)} bytes)",
                file=sys.stderr,
                flush=True,
            )
            print(f"Content preview: {content[:100]}", file=sys.stderr, flush=True)


def validate_mcp_output(output: str) -> tuple[bool, str]:
    """
    Validate that output is valid JSON-RPC or empty.

    Args:
        output: String to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    import json

    if not output or output.isspace():
        return True, ""

    try:
        # Try to parse as JSON
        parsed = json.loads(output)

        # Check if it's valid JSON-RPC 2.0
        if isinstance(parsed, dict):
            if "jsonrpc" in parsed and parsed["jsonrpc"] == "2.0":
                return True, ""
            else:
                return False, "Not a valid JSON-RPC 2.0 message (missing 'jsonrpc': '2.0')"
        else:
            return False, "Not a JSON-RPC message object"

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"


class StdoutValidator:
    """
    Development-mode validator that checks all stdout writes.

    Use this wrapper during development to catch stdout contamination early.
    DO NOT use in production as it adds overhead.
    """

    def __init__(self, original_stdout: Any) -> None:
        self.original_stdout: Any = original_stdout
        self.contaminated: bool = False

    def write(self, text: str) -> None:
        """Write to stdout after validation."""
        if text and not text.isspace():
            is_valid, error = validate_mcp_output(text)
            if not is_valid:
                self.contaminated = True
                print("⚠️  STDOUT CONTAMINATION DETECTED", file=sys.stderr, flush=True)
                print(f"Invalid output: {text[:200]}", file=sys.stderr, flush=True)
                print(f"Error: {error}", file=sys.stderr, flush=True)
                print(
                    "This will cause JSON parsing errors in Claude Desktop!",
                    file=sys.stderr,
                    flush=True,
                )
                # Still write to stderr for visibility
                print(text, file=sys.stderr, flush=True)
                return

        # Write valid output to original stdout
        self.original_stdout.write(text)

    def flush(self) -> None:
        """Flush stdout."""
        self.original_stdout.flush()

    def __getattr__(self, name: str) -> Any:
        """Delegate other attributes to original stdout."""
        return getattr(self.original_stdout, name)


def enable_stdout_validation() -> None:
    """
    Enable stdout validation for development/debugging.

    This wraps stdout with a validator that checks all output.
    Call this AFTER setup_mcp_stdout_safety() if you want validation.

    WARNING: This adds overhead. Only use during development.
    """
    if not isinstance(sys.stdout, StdoutValidator):
        sys.stdout = StdoutValidator(sys.stdout)
        print("✓ Stdout validation enabled (development mode)", file=sys.stderr, flush=True)
