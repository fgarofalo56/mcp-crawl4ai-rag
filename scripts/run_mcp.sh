#!/bin/bash
# Wrapper script for Mac/Linux to run the MCP server with .env file
# This script loads the .env file and runs the MCP server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found in $SCRIPT_DIR"
    echo "Please create a .env file from .env.example"
    echo ""
    exit 1
fi

# Run the Python wrapper script
echo "Starting Crawl4AI RAG MCP Server..."
uv run python run_mcp.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error running MCP server. Please check the error messages above."
    exit 1
fi
