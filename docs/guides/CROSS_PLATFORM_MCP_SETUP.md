# 🔄 Cross-Platform MCP Configuration Guide

Guide for running MCP servers on both Windows (CMD/PowerShell) and WSL from the same project directory.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration Files](#configuration-files)
- [Platform Detection](#platform-detection)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project supports running MCP servers in three environments:
1. **Windows CMD** - Native Windows command prompt
2. **Windows PowerShell** - Windows PowerShell (5.x or 7+)
3. **WSL (Windows Subsystem for Linux)** - Linux environment within Windows

The configuration automatically adapts based on your environment.

---

## Quick Start

### Method 1: Automatic Configuration (Recommended)

The default `.mcp.json` works for both platforms as-is because it uses:
- HTTP/SSE servers (platform-agnostic)
- Cross-platform commands (`npx`, `docker`, `uvx`)

**Just use it directly - no changes needed!**

### Method 2: Platform-Specific Configurations

If you need platform-specific optimizations:

#### On Windows (PowerShell):
```powershell
# Setup Windows-optimized config
.\scripts\setup-mcp-config.ps1 -Platform windows

# Verify
Get-Content .mcp.json
```

#### On Windows (CMD):
```cmd
REM Setup Windows-optimized config
powershell -File scripts\setup-mcp-config.ps1 -Platform windows

REM Verify
type .mcp.json
```

#### On WSL:
```bash
# Setup WSL-optimized config
./scripts/setup-mcp-config.sh wsl

# Verify
cat .mcp.json
```

---

## Configuration Files

### `.mcp.json` (Default - Cross-Platform)
- Works on both Windows and WSL
- Uses platform-agnostic commands
- **Recommended for most users**

### `.mcp.json.windows` (Windows-Specific)
- Optimized for Windows CMD/PowerShell
- Uses `npx.cmd` for better Windows compatibility
- Use if you experience issues with the default config

### `.mcp.json.wsl` (WSL-Specific)
- Optimized for WSL/Linux environments
- Uses standard `npx` command
- Use if you only run Claude Code from WSL

---

## Platform Detection

The launcher scripts automatically detect your environment:

### Windows PowerShell (`scripts\mcp-launcher.ps1`):
```powershell
.\scripts\mcp-launcher.ps1
# Detects: Windows PowerShell
# Activates: .venv\Scripts\Activate.ps1
# Runs: python run_mcp.py
```

### Windows CMD (`scripts\mcp-launcher.cmd`):
```cmd
scripts\mcp-launcher.cmd
REM Detects: Windows CMD
REM Activates: .venv\Scripts\activate.bat
REM Runs: python run_mcp.py
```

### WSL (`scripts/mcp-launcher.sh`):
```bash
./scripts/mcp-launcher.sh
# Detects: WSL (checks /proc/version)
# Converts path: E:\ → /mnt/e/
# Activates: .venv/bin/activate
# Runs: python run_mcp.py
```

---

## Server Configuration Details

### HTTP/SSE Servers (Platform-Agnostic)

These work identically on all platforms:

```json
{
  "crawl4ai-rag": {
    "type": "sse",
    "url": "http://localhost:8051/sse"
  },
  "microsoft-docs-mcp": {
    "type": "http",
    "url": "https://learn.microsoft.com/api/mcp"
  }
}
```

**Why they work everywhere:**
- Use network URLs (localhost, HTTP)
- No file paths or OS-specific commands
- MCP client handles connection

### STDIO Servers (Need Care)

These use OS commands that may differ:

```json
{
  "playwright": {
    "type": "stdio",
    "command": "npx",              // Windows: npx.cmd, WSL: npx
    "args": ["-y", "@executeautomation/playwright-mcp-server"]
  },
  "brave-search": {
    "type": "stdio",
    "command": "npx",              // Cross-platform: works as-is
    "args": ["-y", "@brave/brave-search-mcp-server"],
    "env": {
      "BRAVE_API_KEY": "${BRAVE_API_KEY}"  // Environment variable
    }
  }
}
```

**Cross-platform compatibility:**
- `npx` works on both Windows and WSL (Node.js 16+)
- `docker` works on both if Docker Desktop installed
- `uvx` works on both if `uv` installed
- Environment variables (`${VAR}`) work everywhere

---

## Troubleshooting

### Issue: "npx: command not found" on Windows

**Cause**: Windows CMD may require `npx.cmd` instead of `npx`

**Solution**: Use Windows-specific config
```powershell
.\scripts\setup-mcp-config.ps1 -Platform windows
```

### Issue: Server fails to start in WSL

**Cause**: Virtual environment not activated or wrong path

**Solution**: Use WSL launcher script
```bash
./scripts/mcp-launcher.sh
```

### Issue: Environment variables not found

**Cause**: `.env` file not loaded or missing variables

**Solution**: Verify environment variables
```powershell
# Windows PowerShell
Get-Content .env

# WSL
cat .env
```

Ensure variables are set:
- `BRAVE_API_KEY`
- `AZURE_OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

### Issue: Different ports on Windows vs WSL

**Cause**: Server running in both environments simultaneously

**Solution**: Use different ports
```json
{
  "crawl4ai-rag-windows": {
    "type": "sse",
    "url": "http://localhost:8051/sse"
  },
  "crawl4ai-rag-wsl": {
    "type": "sse",
    "url": "http://localhost:8052/sse"
  }
}
```

Then set port in `.env`:
```bash
# Windows .env
MCP_PORT=8051

# WSL .env (or .env.wsl)
MCP_PORT=8052
```

### Issue: Claude Code can't find servers

**Cause**: Wrong working directory or config file location

**Solution**: Verify paths
```powershell
# Should show .mcp.json in project root
Get-ChildItem .mcp.json

# Should show servers
Get-Content .mcp.json | ConvertFrom-Json | Select -ExpandProperty mcpServers
```

---

## Best Practices

### 1. Use Default Configuration First
The default `.mcp.json` works for 95% of use cases. Only switch to platform-specific configs if you encounter issues.

### 2. Keep Environment Variables in `.env`
Don't hardcode API keys in `.mcp.json`. Use:
```json
{
  "env": {
    "API_KEY": "${API_KEY}"  // Reads from environment
  }
}
```

### 3. Test Both Environments
If you work in both Windows and WSL:
```bash
# Test Windows
.\scripts\mcp-launcher.ps1

# Test WSL
./scripts/mcp-launcher.sh
```

### 4. Document Custom Configurations
If you add platform-specific settings, document why:
```json
{
  "custom-server": {
    "type": "stdio",
    "command": "npx.cmd",  // .cmd required for Windows CMD
    "description": "Custom server - Windows CMD compatibility"
  }
}
```

---

## Additional Resources

- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp)
- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP SDK](https://github.com/anthropics/anthropic-mcp-sdk-python)
- [Project Quick Start](../QUICK_START.md)

---

**Last Updated**: October 28, 2025
**Maintained by**: MCP Crawl4AI RAG Team
