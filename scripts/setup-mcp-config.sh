#!/bin/bash
# Setup MCP configuration for current platform
# Usage: ./scripts/setup-mcp-config.sh [windows|wsl]

set -e

PLATFORM="${1:-wsl}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up MCP configuration for platform: $PLATFORM"

SOURCE_CONFIG="$PROJECT_ROOT/.mcp.json.$PLATFORM"
TARGET_CONFIG="$PROJECT_ROOT/.mcp.json"

if [ -f "$SOURCE_CONFIG" ]; then
    cp "$SOURCE_CONFIG" "$TARGET_CONFIG"
    echo "✓ Copied $SOURCE_CONFIG to $TARGET_CONFIG"
else
    echo "Error: Platform configuration not found: $SOURCE_CONFIG"
    exit 1
fi

echo "✓ MCP configuration setup complete for $PLATFORM"
echo ""
echo "To verify, run:"
echo "  cat .mcp.json"
