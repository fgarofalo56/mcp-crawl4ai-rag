@echo off
REM Cross-platform MCP server launcher for Windows CMD
REM Usage: scripts\mcp-launcher.cmd

setlocal enabledelayedexpansion

REM Get project root (parent of scripts directory)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo Platform: Windows CMD
echo Project root: %PROJECT_ROOT%

REM Activate virtual environment
set "VENV_ACTIVATE=%PROJECT_ROOT%\.venv\Scripts\activate.bat"

if exist "%VENV_ACTIVATE%" (
    echo Activating virtual environment...
    call "%VENV_ACTIVATE%"
) else (
    echo WARNING: Virtual environment not found at %VENV_ACTIVATE%
    echo Creating virtual environment...

    cd /d "%PROJECT_ROOT%"
    uv venv
    call .venv\Scripts\activate.bat
    uv pip install -e ".[dev]"
)

REM Change to project root and run server
cd /d "%PROJECT_ROOT%"
python run_mcp.py %*

endlocal
