#!/bin/bash
# Cross-platform MCP server launcher
# Automatically detects Windows vs WSL and uses correct paths

# Detect environment
if grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null; then
    PLATFORM="wsl"
    PROJECT_ROOT="/mnt/e/Repos/GitHub/mcp-crawl4ai-rag"
else
    PLATFORM="linux"
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

echo "Detected platform: $PLATFORM"
echo "Project root: $PROJECT_ROOT"

# Activate virtual environment
if [ "$PLATFORM" = "wsl" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Run MCP server
cd "$PROJECT_ROOT"
python run_mcp.py "$@"
