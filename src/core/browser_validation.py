"""
Browser Validation Utilities

Provides validation and detection for Playwright browser installations,
handling common issues with browser paths across different deployment scenarios.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def get_global_playwright_browser_path() -> Path | None:
    """
    Get the global Playwright browser installation path.

    Returns:
        Path to global browser directory, or None if not found
    """
    # Windows: %USERPROFILE%\AppData\Local\ms-playwright\
    # Linux/Mac: ~/.cache/ms-playwright/

    if sys.platform == "win32":
        base_path = Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "ms-playwright"
    else:
        base_path = Path.home() / ".cache" / "ms-playwright"

    if base_path.exists():
        return base_path
    return None


def get_venv_playwright_browser_path() -> Path | None:
    """
    Get the virtual environment's Playwright browser installation path.

    Returns:
        Path to venv browser directory, or None if not found
    """
    try:
        import playwright

        playwright_path = Path(playwright.__file__).parent
        # Check for browsers in the package's .local-browsers directory
        local_browsers = playwright_path / "driver" / "package" / ".local-browsers"
        if local_browsers.exists():
            return local_browsers
    except ImportError:
        pass
    return None


def find_chromium_executable(base_path: Path) -> Path | None:
    """
    Find the Chromium executable in a Playwright browser directory.

    Args:
        base_path: Base directory to search for Chromium

    Returns:
        Path to chromium executable, or None if not found
    """
    # Look for chromium-* directories
    for chromium_dir in base_path.glob("chromium-*"):
        if sys.platform == "win32":
            exe_path = chromium_dir / "chrome-win" / "chrome.exe"
        elif sys.platform == "darwin":
            exe_path = (
                chromium_dir / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
            )
        else:
            exe_path = chromium_dir / "chrome-linux" / "chrome"

        if exe_path.exists():
            return exe_path
    return None


def validate_browser_installation() -> tuple[bool, str, Path | None]:
    """
    Validate Playwright browser installation and provide helpful diagnostics.

    Returns:
        Tuple of (is_valid, message, browser_path)
        - is_valid: True if browsers are properly installed
        - message: Diagnostic message (error or success)
        - browser_path: Path to browser directory if found
    """
    # Check for PLAYWRIGHT_BROWSERS_PATH environment variable
    env_browser_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if env_browser_path:
        env_path = Path(env_browser_path)
        if env_path.exists():
            chromium = find_chromium_executable(env_path)
            if chromium:
                return True, f"✓ Browsers found via PLAYWRIGHT_BROWSERS_PATH: {env_path}", env_path
            else:
                return (
                    False,
                    f"⚠️  PLAYWRIGHT_BROWSERS_PATH is set but no browsers found at: {env_path}",
                    None,
                )

    # Check global installation (most common)
    global_path = get_global_playwright_browser_path()
    if global_path and global_path.exists():
        chromium = find_chromium_executable(global_path)
        if chromium:
            # Browsers found globally - need to set environment variable for venv to use them
            return (
                False,
                (
                    f"⚠️  Browsers installed globally at: {global_path}\n"
                    f"   But virtual environment cannot access them.\n"
                    f"   This is a common issue when browsers are installed outside the venv."
                ),
                global_path,
            )

    # Check venv installation
    venv_path = get_venv_playwright_browser_path()
    if venv_path and venv_path.exists():
        chromium = find_chromium_executable(venv_path)
        if chromium:
            return True, f"✓ Browsers found in virtual environment: {venv_path}", venv_path

    # No browsers found anywhere
    return False, "❌ No Playwright browsers found in any location", None


def get_installation_instructions(global_browser_path: Path | None = None) -> str:
    """
    Get platform-specific installation instructions.

    Args:
        global_browser_path: Path to global browser installation (if found)

    Returns:
        Formatted installation instructions
    """
    instructions = [
        "\n" + "=" * 80,
        "🔧 PLAYWRIGHT BROWSER FIX",
        "=" * 80,
    ]

    if global_browser_path:
        instructions.extend(
            [
                "\n✅ GOOD NEWS: Browsers are already installed!",
                f"   Location: {global_browser_path}",
                "\n🔧 SOLUTION (Choose ONE):",
                "\n   Option 1 (RECOMMENDED - Quick Fix):",
                "   Set environment variable to use existing browsers:",
            ]
        )

        if sys.platform == "win32":
            instructions.extend(
                [
                    f'   setx PLAYWRIGHT_BROWSERS_PATH "{global_browser_path}"',
                    "   Then restart your terminal/IDE and try again.",
                    "\n   Option 2 (Alternative):",
                    "   Install browsers in your virtual environment:",
                    "   .venv\\Scripts\\activate",
                    "   playwright install chromium",
                ]
            )
        else:
            instructions.extend(
                [
                    f'   export PLAYWRIGHT_BROWSERS_PATH="{global_browser_path}"',
                    "   # Add to ~/.bashrc or ~/.zshrc to make permanent",
                    "   Then restart your terminal and try again.",
                    "\n   Option 2 (Alternative):",
                    "   Install browsers in your virtual environment:",
                    "   source .venv/bin/activate",
                    "   playwright install chromium",
                ]
            )
    else:
        instructions.extend(
            [
                "\n❌ Browsers not found in any location.",
                "\n🔧 SOLUTION:",
                "   Install Playwright browsers using ONE of these commands:",
                "\n   Option 1 (Recommended - uses uv):",
                "   uv run playwright install chromium",
                "\n   Option 2 (Direct installation):",
            ]
        )

        if sys.platform == "win32":
            instructions.extend(
                [
                    "   .venv\\Scripts\\activate",
                    "   playwright install chromium",
                ]
            )
        else:
            instructions.extend(
                [
                    "   source .venv/bin/activate",
                    "   playwright install chromium",
                ]
            )

    instructions.extend(
        [
            "\n   Option 3 (Docker - browsers pre-installed):",
            "   docker-compose up --build",
            "\n" + "=" * 80 + "\n",
        ]
    )

    return "\n".join(instructions)


def print_browser_diagnostics() -> bool:
    """
    Print comprehensive browser diagnostics and return validity status.

    Returns:
        True if browsers are properly installed and accessible
    """
    is_valid, message, browser_path = validate_browser_installation()

    print(message, file=sys.stderr, flush=True)

    if not is_valid:
        instructions = get_installation_instructions(browser_path)
        print(instructions, file=sys.stderr, flush=True)

    return is_valid
