@echo off
REM Wrapper script for Windows to run the MCP server with .env file
REM This script loads the .env file and runs the MCP server

cd /d "%~dp0"

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found in %cd%
    echo Please create a .env file from .env.example
    echo.
    pause
    exit /b 1
)

REM Run the Python wrapper script
echo Starting Crawl4AI RAG MCP Server...
uv run python run_mcp.py

if errorlevel 1 (
    echo.
    echo Error running MCP server. Please check the error messages above.
    pause
    exit /b 1
)
