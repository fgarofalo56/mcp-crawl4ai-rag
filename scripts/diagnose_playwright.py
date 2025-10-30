#!/usr/bin/env python
"""
Diagnostic script to check Playwright installation and browser availability.
Run this to troubleshoot Crawl4AI browser initialization issues.

Usage:
    python scripts/diagnose_playwright.py
    # Or from any directory:
    uv run python scripts/diagnose_playwright.py
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for console output on Windows
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def check_playwright_installed():
    """Check if Playwright package is installed."""
    print_header("1. Checking Playwright Package Installation")
    try:
        import playwright

        print("✅ Playwright package is installed")
        # Get version from __version__ if available, otherwise skip
        try:
            print(f"   Version: {playwright.__version__}")
        except AttributeError:
            print("   Version: (version attribute not available)")
        print(f"   Location: {playwright.__file__}")
        return True
    except ImportError:
        print("❌ Playwright package is NOT installed")
        print("\nInstall with: uv pip install playwright")
        return False


def check_browser_validation_module():
    """Check if the browser validation module can detect browsers."""
    print_header("2. Running Browser Validation Module")
    try:
        # Add src to path if needed
        src_path = Path(__file__).parent.parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from core.browser_validation import (
            get_global_playwright_browser_path,
            get_venv_playwright_browser_path,
            validate_browser_installation,
        )

        # Check environment variable
        env_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
        if env_path:
            print(f"📍 PLAYWRIGHT_BROWSERS_PATH: {env_path}")
            if Path(env_path).exists():
                print("   ✅ Directory exists")
            else:
                print("   ❌ Directory does NOT exist")
        else:
            print("📍 PLAYWRIGHT_BROWSERS_PATH: Not set")

        # Check global installation
        global_path = get_global_playwright_browser_path()
        if global_path:
            print(f"\n📍 Global browser path: {global_path}")
            if global_path.exists():
                print("   ✅ Directory exists")
                # List contents
                chromium_dirs = list(global_path.glob("chromium-*"))
                if chromium_dirs:
                    print(f"   ✅ Found {len(chromium_dirs)} Chromium installation(s)")
                else:
                    print("   ⚠️  No Chromium installations found")
            else:
                print("   ❌ Directory does NOT exist")
        else:
            print("\n📍 Global browser path: Not found")

        # Check venv installation
        venv_path = get_venv_playwright_browser_path()
        if venv_path:
            print(f"\n📍 Venv browser path: {venv_path}")
            if venv_path.exists():
                print("   ✅ Directory exists")
                # List contents
                chromium_dirs = list(venv_path.glob("chromium-*"))
                if chromium_dirs:
                    print(f"   ✅ Found {len(chromium_dirs)} Chromium installation(s)")
                else:
                    print("   ⚠️  No Chromium installations found")
            else:
                print("   ❌ Directory does NOT exist")
        else:
            print("\n📍 Venv browser path: Not found")

        # Run full validation
        print("\n🔍 Running full browser validation...")
        is_valid, message, browser_path = validate_browser_installation()
        print(f"\nValidation Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        print(f"Message: {message}")
        if browser_path:
            print(f"Browser Path: {browser_path}")

        return is_valid
    except Exception as e:
        print(f"❌ Browser validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_playwright_browsers():
    """Check if Playwright browsers are installed (legacy check)."""
    print_header("3. Checking Playwright Browser Installation (Direct Check)")
    try:
        import playwright

        playwright_path = Path(playwright.__file__).parent
        browsers_path = playwright_path / "driver" / "package" / ".local-browsers"

        print(f"Browser directory: {browsers_path}")

        if not browsers_path.exists():
            print("❌ Browser directory does NOT exist")
            print("\n🔧 SOLUTION: Install browsers with:")
            print("   uv run playwright install chromium")
            return False

        # Check for Chromium
        chromium_dirs = list(browsers_path.glob("chromium-*"))
        if chromium_dirs:
            print(f"✅ Found Chromium installations: {len(chromium_dirs)}")
            for chromium_dir in chromium_dirs:
                print(f"   - {chromium_dir.name}")

                # Check for chrome executable based on platform
                if sys.platform == "win32":
                    chrome_exe = chromium_dir / "chrome-win" / "chrome.exe"
                elif sys.platform == "darwin":
                    chrome_exe = (
                        chromium_dir
                        / "chrome-mac"
                        / "Chromium.app"
                        / "Contents"
                        / "MacOS"
                        / "Chromium"
                    )
                else:
                    chrome_exe = chromium_dir / "chrome-linux" / "chrome"

                if chrome_exe.exists():
                    print(f"     ✅ Executable found: {chrome_exe}")
                else:
                    print(f"     ❌ Executable missing: {chrome_exe}")
        else:
            print("❌ No Chromium installations found")
            print("\n🔧 SOLUTION: Install Chromium with:")
            print("   uv run playwright install chromium")
            return False

        return True
    except Exception as e:
        print(f"❌ Error checking browsers: {e}")
        return False


def test_browser_launch():
    """Try to launch a Playwright browser."""
    print_header("4. Testing Browser Launch")
    try:
        import asyncio

        from playwright.async_api import async_playwright

        async def launch_test():
            try:
                async with async_playwright() as p:
                    print("Launching Chromium browser...")
                    browser = await p.chromium.launch(headless=True)
                    print("✅ Browser launched successfully!")

                    page = await browser.new_page()
                    print("✅ Created new page successfully!")

                    await browser.close()
                    print("✅ Browser closed successfully!")
                    return True
            except Exception as e:
                print(f"❌ Browser launch failed: {e}")
                print(f"\nError type: {type(e).__name__}")
                import traceback

                traceback.print_exc()
                return False

        result = asyncio.run(launch_test())
        return result
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_crawl4ai():
    """Try to initialize Crawl4AI."""
    print_header("5. Testing Crawl4AI Initialization")
    try:
        import asyncio

        from crawl4ai import AsyncWebCrawler, BrowserConfig

        async def crawl4ai_test():
            try:
                print("Creating browser configuration...")
                config = BrowserConfig(headless=True, verbose=False)

                print("Initializing AsyncWebCrawler...")
                crawler = AsyncWebCrawler(config=config)

                print("Starting crawler...")
                await crawler.__aenter__()
                print("✅ Crawl4AI initialized successfully!")

                print("Cleaning up...")
                await crawler.__aexit__(None, None, None)
                print("✅ Crawl4AI cleaned up successfully!")
                return True
            except Exception as e:
                print(f"❌ Crawl4AI initialization failed: {e}")
                import traceback

                traceback.print_exc()
                return False

        result = asyncio.run(crawl4ai_test())
        return result
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_permissions():
    """Check if we have write permissions in the virtual environment."""
    print_header("6. Checking Permissions")
    try:
        venv_path = Path(sys.prefix)
        print(f"Virtual environment: {venv_path}")

        # Try to create a test file
        test_file = venv_path / "test_write_permission.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("✅ Write permissions OK")
            return True
        except PermissionError:
            print("❌ No write permissions in virtual environment")
            print("\n🔧 SOLUTION: Run as administrator or check folder permissions")
            return False
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
        return False


def print_installation_instructions(all_passed: bool):
    """Print helpful installation instructions based on results."""
    if all_passed:
        return

    print_header("INSTALLATION INSTRUCTIONS")
    print("\n📝 To fix browser installation issues, try these steps IN ORDER:\n")

    print("STEP 1: Quick Fix - Install browsers in virtual environment")
    print("=" * 80)
    if sys.platform == "win32":
        print("  uv run playwright install chromium")
        print("\n  Alternative (manual activation):")
        print("  .venv\\Scripts\\activate")
        print("  playwright install chromium")
        print("  deactivate")
    else:
        print("  uv run playwright install chromium")
        print("\n  Alternative (manual activation):")
        print("  source .venv/bin/activate")
        print("  playwright install chromium")
        print("  deactivate")

    print("\n\nSTEP 2: If browsers are installed globally but not accessible")
    print("=" * 80)
    if sys.platform == "win32":
        print("  Set environment variable (PowerShell as Administrator):")
        print('  [System.Environment]::SetEnvironmentVariable("PLAYWRIGHT_BROWSERS_PATH", ')
        print('      "$env:USERPROFILE\\AppData\\Local\\ms-playwright", "User")')
        print("\n  Then restart your terminal/IDE")
    else:
        print("  Add to ~/.bashrc or ~/.zshrc:")
        print('  export PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright"')
        print("\n  Then run: source ~/.bashrc (or ~/.zshrc)")

    print("\n\nSTEP 3: Complete reinstall (if above steps don't work)")
    print("=" * 80)
    if sys.platform == "win32":
        print("  Remove-Item -Recurse -Force .venv")
        print("  uv venv")
        print("  uv pip install -e .[dev]")
        print("  uv run playwright install chromium")
    else:
        print("  rm -rf .venv")
        print("  uv venv")
        print("  uv pip install -e .[dev]")
        print("  uv run playwright install chromium")

    print("\n\nSTEP 4: Docker (if local installation keeps failing)")
    print("=" * 80)
    print("  docker-compose up --build")
    print("  # Browsers are pre-installed in Docker container")


def main():
    """Run all diagnostic checks."""
    print("\n" + "=" * 80)
    print("  CRAWL4AI PLAYWRIGHT DIAGNOSTIC TOOL")
    print("=" * 80)
    print(f"\nPython: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Virtual Env: {sys.prefix}")
    print(f"Platform: {sys.platform}")

    results = {
        "Playwright Package": check_playwright_installed(),
        "Browser Validation Module": check_browser_validation_module(),
        "Direct Browser Check": check_playwright_browsers(),
        "Permissions": check_permissions(),
        "Browser Launch Test": test_browser_launch(),
        "Crawl4AI Test": test_crawl4ai(),
    }

    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} - {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All checks passed! Your Playwright installation is working correctly.")
        print("   If MCP server still fails, check your .env configuration.")
        print("\n   To start the MCP server:")
        print("   python run_mcp.py")
    else:
        print("\n⚠️  Some checks failed. See instructions below to fix.")
        print_installation_instructions(all_passed)


if __name__ == "__main__":
    main()
