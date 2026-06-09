"""
Tests for Browser Validation Module

Tests browser path detection, validation logic, and error messaging
for various browser installation scenarios.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.browser_validation import (
    find_chromium_executable,
    get_global_playwright_browser_path,
    get_installation_instructions,
    get_venv_playwright_browser_path,
    validate_browser_installation,
)


class TestBrowserPathDetection:
    """Test browser path detection functions."""

    def test_get_global_playwright_browser_path_windows(self):
        """Test global browser path detection on Windows."""
        with patch("sys.platform", "win32"):
            with patch.dict(os.environ, {"USERPROFILE": "C:\\Users\\TestUser"}):
                expected_path = Path("C:\\Users\\TestUser\\AppData\\Local\\ms-playwright")
                with patch("pathlib.Path.exists", return_value=True):
                    path = get_global_playwright_browser_path()
                    assert path == expected_path

    def test_get_global_playwright_browser_path_linux(self):
        """Test global browser path detection on Linux."""
        with patch("sys.platform", "linux"):
            with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
                expected_path = Path("/home/testuser/.cache/ms-playwright")
                with patch("pathlib.Path.exists", return_value=True):
                    path = get_global_playwright_browser_path()
                    assert path == expected_path

    def test_get_global_playwright_browser_path_mac(self):
        """Test global browser path detection on Mac."""
        with patch("sys.platform", "darwin"):
            with patch("pathlib.Path.home", return_value=Path("/Users/testuser")):
                expected_path = Path("/Users/testuser/.cache/ms-playwright")
                with patch("pathlib.Path.exists", return_value=True):
                    path = get_global_playwright_browser_path()
                    assert path == expected_path


class TestChromiumExecutableDetection:
    """Test Chromium executable detection."""

    def test_find_chromium_executable_windows(self, tmp_path):
        """Test finding Chromium executable on Windows."""
        # Create mock directory structure
        chromium_dir = tmp_path / "chromium-1187"
        chrome_dir = chromium_dir / "chrome-win"
        chrome_dir.mkdir(parents=True)
        chrome_exe = chrome_dir / "chrome.exe"
        chrome_exe.touch()

        with patch("sys.platform", "win32"):
            result = find_chromium_executable(tmp_path)
            assert result == chrome_exe

    def test_find_chromium_executable_linux(self, tmp_path):
        """Test finding Chromium executable on Linux."""
        # Create mock directory structure
        chromium_dir = tmp_path / "chromium-1187"
        chrome_dir = chromium_dir / "chrome-linux"
        chrome_dir.mkdir(parents=True)
        chrome_exe = chrome_dir / "chrome"
        chrome_exe.touch()

        with patch("sys.platform", "linux"):
            result = find_chromium_executable(tmp_path)
            assert result == chrome_exe

    def test_find_chromium_executable_not_found(self, tmp_path):
        """Test when Chromium executable is not found."""
        with patch("sys.platform", "win32"):
            result = find_chromium_executable(tmp_path)
            assert result is None


class TestBrowserValidation:
    """Test browser validation logic."""

    def test_validate_with_env_var_set_and_browsers_exist(self, tmp_path):
        """Test validation when PLAYWRIGHT_BROWSERS_PATH is set and browsers exist."""
        # Create mock browser structure
        chromium_dir = tmp_path / "chromium-1187"
        chrome_dir = chromium_dir / "chrome-win"
        chrome_dir.mkdir(parents=True)
        chrome_exe = chrome_dir / "chrome.exe"
        chrome_exe.touch()

        with patch("sys.platform", "win32"):
            with patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(tmp_path)}):
                is_valid, message, browser_path = validate_browser_installation()
                assert is_valid is True
                assert "PLAYWRIGHT_BROWSERS_PATH" in message
                assert browser_path == tmp_path

    def test_validate_with_env_var_set_but_no_browsers(self, tmp_path):
        """Test validation when PLAYWRIGHT_BROWSERS_PATH is set but no browsers found."""
        with patch("sys.platform", "win32"):
            with patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(tmp_path)}):
                is_valid, message, browser_path = validate_browser_installation()
                assert is_valid is False
                assert "PLAYWRIGHT_BROWSERS_PATH is set but no browsers found" in message
                assert browser_path is None

    def test_validate_with_global_browsers_no_env_var(self, tmp_path):
        """Test validation when browsers are global but environment variable not set."""
        # Create mock global browser structure
        chromium_dir = tmp_path / "chromium-1187"
        chrome_dir = chromium_dir / "chrome-win"
        chrome_dir.mkdir(parents=True)
        chrome_exe = chrome_dir / "chrome.exe"
        chrome_exe.touch()

        with (
            patch("sys.platform", "win32"),
            patch(
                "core.browser_validation.get_global_playwright_browser_path",
                return_value=tmp_path,
            ),
        ):
            is_valid, message, browser_path = validate_browser_installation()
            assert is_valid is False
            assert "globally" in message.lower()
            assert browser_path == tmp_path

    def test_validate_with_no_browsers_anywhere(self):
        """Test validation when no browsers are found anywhere."""
        with (
            patch("sys.platform", "win32"),
            patch(
                "core.browser_validation.get_global_playwright_browser_path",
                return_value=None,
            ),
            patch(
                "core.browser_validation.get_venv_playwright_browser_path",
                return_value=None,
            ),
        ):
            is_valid, message, browser_path = validate_browser_installation()
            assert is_valid is False
            assert "No Playwright browsers found" in message
            assert browser_path is None


class TestInstallationInstructions:
    """Test installation instruction generation."""

    def test_instructions_with_global_browsers_windows(self, tmp_path):
        """Test instructions when global browsers exist on Windows."""
        with patch("sys.platform", "win32"):
            instructions = get_installation_instructions(tmp_path)
            assert "GOOD NEWS" in instructions
            assert "setx PLAYWRIGHT_BROWSERS_PATH" in instructions
            assert ".venv\\Scripts\\activate" in instructions

    def test_instructions_with_global_browsers_linux(self, tmp_path):
        """Test instructions when global browsers exist on Linux/Mac."""
        with patch("sys.platform", "linux"):
            instructions = get_installation_instructions(tmp_path)
            assert "GOOD NEWS" in instructions
            assert "export PLAYWRIGHT_BROWSERS_PATH" in instructions
            assert "source .venv/bin/activate" in instructions

    def test_instructions_with_no_global_browsers_windows(self):
        """Test instructions when no global browsers exist on Windows."""
        with patch("sys.platform", "win32"):
            instructions = get_installation_instructions(None)
            assert "Browsers not found" in instructions
            assert "uv run playwright install chromium" in instructions
            assert ".venv\\Scripts\\activate" in instructions

    def test_instructions_with_no_global_browsers_linux(self):
        """Test instructions when no global browsers exist on Linux/Mac."""
        with patch("sys.platform", "linux"):
            instructions = get_installation_instructions(None)
            assert "Browsers not found" in instructions
            assert "uv run playwright install chromium" in instructions
            assert "source .venv/bin/activate" in instructions

    def test_instructions_include_docker_option(self):
        """Test that all instructions include Docker as an option."""
        with patch("sys.platform", "win32"):
            instructions = get_installation_instructions(None)
            assert "docker compose up --build" in instructions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
