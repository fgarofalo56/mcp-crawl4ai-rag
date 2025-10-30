#!/usr/bin/env python
"""
Wrapper script to load .env before running MCP server.
This script ensures all environment variables are properly loaded
before starting the MCP server, making it easier to use with Claude Desktop.
"""

import asyncio
import os
import socket
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv

# Suppress Pydantic v2 deprecation warnings from dependencies
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*class-based `config` is deprecated.*"
)
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*The `gotrue` package is deprecated.*"
)


def print_info(*args, **kwargs):
    """Print to stderr to avoid breaking stdio JSON-RPC protocol."""
    print(*args, file=sys.stderr, **kwargs)


def find_free_port():
    """Find an available port on the system."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def main_wrapper():
    """Entry point that loads .env file and runs the MCP server"""

    # ⚠️  CRITICAL: Set up stdout safety FIRST, before any other imports
    # This prevents libraries from writing to stdout and breaking MCP protocol
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from stdout_safety import setup_mcp_stdout_safety

    setup_mcp_stdout_safety()

    # Suppress Pydantic and other dependency warnings
    os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

    # Get project root directory
    project_root = Path(__file__).resolve().parent

    # Try to load .env from multiple locations (in order of preference)
    possible_env_paths = [
        project_root / ".env",  # Project root (primary location)
        Path.cwd() / ".env",  # Current directory (if running from elsewhere)
        Path.home() / ".crawl4ai-rag.env",  # User home directory (global config)
    ]

    env_loaded = False
    for env_path in possible_env_paths:
        if env_path.exists():
            print_info(f"Loading environment from: {env_path}")
            load_dotenv(env_path, override=True)
            env_loaded = True
            break

    if not env_loaded:
        print_info("Warning: No .env file found. Using system environment variables.")
        print_info("Searched locations:")
        for path in possible_env_paths:
            print_info(f"  - {path}")

    # Force stdio transport even if .env sets a different value.
    os.environ["TRANSPORT"] = "stdio"
    os.environ["HOST"] = ""
    # NEO4J_URI is set from .env file - don't override it here

    # Debug: Print Neo4j configuration (without password)
    print_info(f"DEBUG: USE_KNOWLEDGE_GRAPH={os.getenv('USE_KNOWLEDGE_GRAPH')}")
    print_info(f"DEBUG: NEO4J_USER={os.getenv('NEO4J_USER')}")
    print_info(f"DEBUG: NEO4J_PASSWORD={'***' if os.getenv('NEO4J_PASSWORD') else 'NOT SET'}")

    # Verify critical environment variables
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print_info("\n⚠️  Warning: Missing required environment variables:")
        for var in missing_vars:
            print_info(f"  - {var}")
        print_info("\nPlease ensure these are set in your .env file or system environment.")
        print_info("Continuing anyway, but some features may not work properly.\n")

    # Add src to path
    sys.path.insert(0, str(project_root / "src"))

    # Set a free port
    free_port = find_free_port()
    os.environ["PORT"] = str(free_port)
    print_info(f"Using port: {free_port}")

    try:
        # Import and run the main function from the new modular server
        # Note: src is already in sys.path, so import directly from server module
        from server import main

        asyncio.run(main())
    except ImportError as e:
        print_info(f"Error importing MCP server: {e}")
        print_info("\nPlease ensure you have installed the dependencies:")
        print_info("  uv pip install -e .")
        print_info("  crawl4ai-setup")
        print_info(f"\nDebug: sys.path includes: {sys.path[0]}")
    except Exception as e:
        print_info(f"An error occurred while running the MCP server: {e}")
        import traceback

        print_info("\nFull traceback:")
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main_wrapper()
