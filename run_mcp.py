#!/usr/bin/env python
"""
Wrapper script to load .env before running MCP server.
This script ensures all environment variables are properly loaded
before starting the MCP server, making it easier to use with Claude Desktop.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

def main_wrapper():
    """Entry point that loads .env file and runs the MCP server"""
    
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
            print(f"Loading environment from: {env_path}")
            load_dotenv(env_path, override=True)
            env_loaded = True
            break
    
    if not env_loaded:
        print("Warning: No .env file found. Using system environment variables.")
        print("Searched locations:")
        for path in possible_env_paths:
            print(f"  - {path}")
    
    # Verify critical environment variables
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\n⚠️  Warning: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease ensure these are set in your .env file or system environment.")
        print("Continuing anyway, but some features may not work properly.\n")
    
    # Add src to path
    sys.path.insert(0, str(project_root / "src"))
    
    try:
        # Import and run the main function
        from crawl4ai_mcp import main
        asyncio.run(main())
    except ImportError as e:
        print(f"Error importing MCP server: {e}")
        print("\nPlease ensure you have installed the dependencies:")
        print("  uv pip install -e .")
        print("  crawl4ai-setup")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nMCP server stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error running MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_wrapper()
