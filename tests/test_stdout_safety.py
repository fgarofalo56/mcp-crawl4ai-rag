"""
Tests for stdout safety module.

This test suite verifies that the stdout_safety module properly:
1. Configures logging to use stderr only
2. Sets environment variables to suppress library output
3. Validates MCP output correctly
4. Redirects stdout to stderr when needed
5. Suppresses third-party library logging

Author: Claude
Date: October 17, 2025
"""

import logging
import os
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to path for imports
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from stdout_safety import (
    StderrRedirector,
    StdoutValidator,
    configure_logging_for_mcp,
    setup_mcp_stdout_safety,
    suppress_stdout,
    validate_mcp_output,
)


class TestStderrRedirector:
    """Test the StderrRedirector context manager."""

    def test_redirector_redirects_stdout_to_stderr(self):
        """Test that stdout is redirected to stderr within context."""
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        with StderrRedirector():
            # Inside context, stdout should be stderr
            assert sys.stdout is original_stderr
            assert sys.stdout is not original_stdout

        # After context, stdout should be restored
        assert sys.stdout is original_stdout

    def test_redirector_preserves_stderr(self):
        """Test that stderr is unchanged."""
        original_stderr = sys.stderr

        with StderrRedirector():
            assert sys.stderr is original_stderr

        assert sys.stderr is original_stderr

    def test_redirector_restores_stdout_on_exception(self):
        """Test that stdout is restored even if exception occurs."""
        original_stdout = sys.stdout

        with pytest.raises(ValueError), StderrRedirector():
            raise ValueError("Test exception")

        # stdout should be restored despite exception
        assert sys.stdout is original_stdout


class TestSuppressStdout:
    """Test the suppress_stdout context manager."""

    def test_suppress_stdout_discards_output(self, capsys):
        """Test that stdout output is discarded within context."""
        with suppress_stdout():
            print("This should be suppressed")

        captured = capsys.readouterr()
        # Output should not appear in stdout or stderr
        assert "This should be suppressed" not in captured.out
        assert "This should be suppressed" not in captured.err

    def test_suppress_stdout_restores_after_context(self, capsys):
        """Test that stdout is restored after context."""
        with suppress_stdout():
            print("Suppressed")

        print("Not suppressed")

        captured = capsys.readouterr()
        assert "Not suppressed" in captured.out
        assert "Suppressed" not in captured.out

    def test_suppress_stdout_handles_exception(self, capsys):
        """Test that stdout is restored even on exception."""
        with pytest.raises(RuntimeError), suppress_stdout():
            print("Before exception")
            raise RuntimeError("Test error")

        print("After exception")
        captured = capsys.readouterr()
        assert "After exception" in captured.out


class TestConfigureLoggingForMCP:
    """Test logging configuration for MCP."""

    def test_configure_logging_uses_stderr(self, capsys):
        """Test that logging is configured to use stderr."""
        configure_logging_for_mcp()

        logger = logging.getLogger("test_logger")
        logger.warning("Test warning message")

        captured = capsys.readouterr()
        # Logging should go to stderr, not stdout
        assert "Test warning message" in captured.err
        assert "Test warning message" not in captured.out

    def test_configure_logging_sets_root_level(self):
        """Test that root logger level is set to WARNING."""
        configure_logging_for_mcp()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING

    def test_configure_logging_suppresses_third_party(self, capsys):
        """Test that third-party loggers are set to ERROR level."""
        configure_logging_for_mcp()

        # Test httpx logger
        httpx_logger = logging.getLogger("httpx")
        assert httpx_logger.level == logging.ERROR

        # Test that INFO messages are suppressed
        httpx_logger.info("This should be suppressed")
        captured = capsys.readouterr()
        assert "This should be suppressed" not in captured.err

        # Test that ERROR messages still appear
        httpx_logger.error("This should appear")
        captured = capsys.readouterr()
        assert "This should appear" in captured.err

    def test_configure_logging_no_propagation(self):
        """Test that third-party loggers don't propagate to root."""
        configure_logging_for_mcp()

        # Check that third-party loggers have propagate=False
        for logger_name in ["httpx", "crawl4ai", "neo4j"]:
            logger = logging.getLogger(logger_name)
            assert logger.propagate is False


class TestSetupMCPStdoutSafety:
    """Test the main setup function."""

    def test_setup_sets_environment_variables(self):
        """Test that required environment variables are set."""
        setup_mcp_stdout_safety()

        # Check critical environment variables
        assert os.getenv("PYTHONIOENCODING") == "utf-8"
        assert os.getenv("PYTHONUNBUFFERED") == "1"
        assert os.getenv("HTTPX_LOG_LEVEL") == "ERROR"
        assert os.getenv("PLAYWRIGHT_BROWSERS_PATH") == "0"
        assert os.getenv("DEBUG") == ""

    def test_setup_configures_logging(self, capsys):
        """Test that setup configures logging correctly."""
        setup_mcp_stdout_safety()

        logger = logging.getLogger()
        logger.warning("Test after setup")

        captured = capsys.readouterr()
        assert "Test after setup" in captured.err

    def test_setup_is_idempotent(self):
        """Test that calling setup multiple times is safe."""
        setup_mcp_stdout_safety()
        setup_mcp_stdout_safety()  # Should not error

        # Environment variables should still be set correctly
        assert os.getenv("PYTHONIOENCODING") == "utf-8"
        assert os.getenv("HTTPX_LOG_LEVEL") == "ERROR"


class TestValidateMCPOutput:
    """Test MCP output validation."""

    def test_validate_empty_string(self):
        """Test that empty string is valid."""
        is_valid, error = validate_mcp_output("")
        assert is_valid is True
        assert error == ""

    def test_validate_whitespace_only(self):
        """Test that whitespace-only string is valid."""
        is_valid, error = validate_mcp_output("   \n\t  ")
        assert is_valid is True
        assert error == ""

    def test_validate_valid_jsonrpc(self):
        """Test that valid JSON-RPC 2.0 message is valid."""
        message = '{"jsonrpc": "2.0", "method": "test", "id": 1}'
        is_valid, error = validate_mcp_output(message)
        assert is_valid is True
        assert error == ""

    def test_validate_invalid_json(self):
        """Test that invalid JSON is rejected."""
        message = "{invalid json"
        is_valid, error = validate_mcp_output(message)
        assert is_valid is False
        assert "Invalid JSON" in error

    def test_validate_json_without_jsonrpc_field(self):
        """Test that JSON without 'jsonrpc' field is rejected."""
        message = '{"method": "test", "id": 1}'
        is_valid, error = validate_mcp_output(message)
        assert is_valid is False
        assert "Not a valid JSON-RPC 2.0 message" in error

    def test_validate_jsonrpc_wrong_version(self):
        """Test that JSON-RPC with wrong version is rejected."""
        message = '{"jsonrpc": "1.0", "method": "test", "id": 1}'
        is_valid, error = validate_mcp_output(message)
        assert is_valid is False
        assert "Not a valid JSON-RPC 2.0 message" in error

    def test_validate_json_array(self):
        """Test that JSON array (not object) is rejected."""
        message = '[{"jsonrpc": "2.0"}]'
        is_valid, error = validate_mcp_output(message)
        assert is_valid is False
        assert "Not a JSON-RPC message object" in error

    def test_validate_contaminated_output(self):
        """Test that contaminated output (like [FETCH]) is rejected."""
        message = "[FETCH] Downloading page..."
        is_valid, error = validate_mcp_output(message)
        assert is_valid is False
        assert "Invalid JSON" in error


class TestStdoutValidator:
    """Test the StdoutValidator wrapper."""

    def test_validator_allows_valid_jsonrpc(self, capsys):
        """Test that valid JSON-RPC passes through."""
        mock_stdout = StringIO()
        validator = StdoutValidator(mock_stdout)

        message = '{"jsonrpc": "2.0", "method": "test", "id": 1}'
        validator.write(message)

        # Should write to original stdout
        assert message in mock_stdout.getvalue()

    def test_validator_blocks_invalid_output(self, capsys):
        """Test that invalid output is blocked."""
        mock_stdout = StringIO()
        validator = StdoutValidator(mock_stdout)

        invalid_message = "[FETCH] Downloading..."
        validator.write(invalid_message)

        # Should NOT write to original stdout
        assert invalid_message not in mock_stdout.getvalue()

        # Should write warning to stderr
        captured = capsys.readouterr()
        assert "STDOUT CONTAMINATION DETECTED" in captured.err

    def test_validator_allows_empty_string(self):
        """Test that empty string passes through."""
        mock_stdout = StringIO()
        validator = StdoutValidator(mock_stdout)

        validator.write("")
        # Should not cause any errors
        assert mock_stdout.getvalue() == ""

    def test_validator_allows_whitespace(self):
        """Test that whitespace passes through."""
        mock_stdout = StringIO()
        validator = StdoutValidator(mock_stdout)

        validator.write("   \n")
        # Whitespace should pass through (newlines are needed for protocol)
        assert "   \n" in mock_stdout.getvalue()

    def test_validator_flush(self):
        """Test that flush is delegated to original stdout."""
        mock_stdout = MagicMock()
        validator = StdoutValidator(mock_stdout)

        validator.flush()
        mock_stdout.flush.assert_called_once()

    def test_validator_contamination_flag(self, capsys):
        """Test that contamination flag is set correctly."""
        mock_stdout = StringIO()
        validator = StdoutValidator(mock_stdout)

        assert validator.contaminated is False

        # Write invalid output
        validator.write("[FETCH] test")
        assert validator.contaminated is True


class TestIntegration:
    """Integration tests for stdout safety."""

    def test_full_setup_prevents_stdout_contamination(self, capsys):
        """Test that full setup prevents stdout contamination."""
        setup_mcp_stdout_safety()

        # Try to log from a third-party logger
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.info("This should not appear")

        captured = capsys.readouterr()
        # Should not appear in stdout OR stderr (suppressed)
        assert "This should not appear" not in captured.out
        assert "This should not appear" not in captured.err

    def test_logging_goes_to_stderr_not_stdout(self, capsys):
        """Test that all logging goes to stderr."""
        setup_mcp_stdout_safety()

        # Log from root logger
        logging.getLogger().warning("Root logger message")

        # Log from third-party logger (error level to bypass suppression)
        logging.getLogger("crawl4ai").error("Third-party error")

        captured = capsys.readouterr()

        # Both should be in stderr
        assert "Root logger message" in captured.err
        assert "Third-party error" in captured.err

        # Neither should be in stdout
        assert "Root logger message" not in captured.out
        assert "Third-party error" not in captured.out

    def test_environment_variables_persist(self):
        """Test that environment variables remain set."""
        setup_mcp_stdout_safety()

        # Simulate some other code running
        _ = os.getenv("HOME")  # Access env vars

        # Check that our vars are still set
        assert os.getenv("PYTHONIOENCODING") == "utf-8"
        assert os.getenv("HTTPX_LOG_LEVEL") == "ERROR"
        assert os.getenv("PLAYWRIGHT_BROWSERS_PATH") == "0"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
