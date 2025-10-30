# Scripts Directory

Utility scripts for development, deployment, and cross-platform support.

## MCP Configuration Scripts

### `setup-mcp-config.ps1` (Windows PowerShell)
Setup platform-specific MCP configuration for Windows.

```powershell
# Usage
.\scripts\setup-mcp-config.ps1 -Platform windows

# What it does
# 1. Copies .mcp.json.windows → .mcp.json
# 2. Optimizes for Windows CMD/PowerShell (npx.cmd)
```

### `setup-mcp-config.sh` (Bash/WSL)
Setup platform-specific MCP configuration for WSL/Linux.

```bash
# Usage
./scripts/setup-mcp-config.sh wsl

# What it does
# 1. Copies .mcp.json.wsl → .mcp.json
# 2. Optimizes for WSL/Linux environments
```

## MCP Launcher Scripts

### `mcp-launcher.ps1` (Windows PowerShell)
Cross-platform MCP server launcher for Windows PowerShell.

```powershell
# Usage
.\scripts\mcp-launcher.ps1

# What it does
# 1. Detects Windows PowerShell environment
# 2. Activates .venv\Scripts\Activate.ps1
# 3. Runs python run_mcp.py
```

### `mcp-launcher.cmd` (Windows CMD)
Cross-platform MCP server launcher for Windows CMD.

```cmd
REM Usage
scripts\mcp-launcher.cmd

REM What it does
REM 1. Detects Windows CMD environment
REM 2. Activates .venv\Scripts\activate.bat
REM 3. Runs python run_mcp.py
```

### `mcp-launcher.sh` (Bash/WSL)
Cross-platform MCP server launcher for WSL/Linux.

```bash
# Usage
./scripts/mcp-launcher.sh

# What it does
# 1. Detects WSL vs native Linux
# 2. Converts Windows paths to WSL paths
# 3. Activates .venv/bin/activate
# 4. Runs python run_mcp.py
```

## Docker Scripts

### `run_docker.ps1` (Windows PowerShell)
Build and run Docker containers with Neo4j support.

```powershell
# Usage
.\scripts\run_docker.ps1

# What it does
# 1. Builds Docker image from Dockerfile
# 2. Starts containers via docker-compose
# 3. Includes Neo4j for knowledge graph features
```

## Task Management Scripts

### `task_helper.py`
Helper script for task creation and management.

```bash
# Usage
python scripts/task_helper.py create-refactor
python scripts/task_helper.py create-feature
python scripts/task_helper.py list-tasks

# What it does
# - Creates task files from templates
# - Lists active tasks
# - Updates task status
```

### `sprint_helper.py`
Helper script for sprint planning and tracking.

```bash
# Usage
python scripts/sprint_helper.py create-sprint
python scripts/sprint_helper.py update-metrics
python scripts/sprint_helper.py sprint-status

# What it does
# - Creates sprint planning files
# - Updates sprint metrics
# - Generates sprint status reports
```

## Validation Scripts

### `validate_deployment.py`
Validates deployment configuration and environment.

```bash
# Usage
python scripts/validate_deployment.py

# What it does
# 1. Checks .env configuration
# 2. Validates API credentials
# 3. Tests database connections
# 4. Verifies MCP server health
```

### `diagnose_playwright.py`
Diagnoses Playwright installation and browser issues.

```bash
# Usage
python scripts/diagnose_playwright.py

# What it does
# 1. Checks Playwright installation
# 2. Validates browser binaries
# 3. Tests browser launch
# 4. Reports compatibility issues
```

## Quick Reference

### Common Workflows

#### Setup for Windows Development
```powershell
# 1. Setup config
.\scripts\setup-mcp-config.ps1 -Platform windows

# 2. Validate environment
python scripts\validate_deployment.py

# 3. Run server
.\scripts\mcp-launcher.ps1
```

#### Setup for WSL Development
```bash
# 1. Setup config
./scripts/setup-mcp-config.sh wsl

# 2. Validate environment
python scripts/validate_deployment.py

# 3. Run server
./scripts/mcp-launcher.sh
```

#### Docker Deployment
```powershell
# Windows
.\scripts\run_docker.ps1

# WSL (from /mnt/e/Repos/GitHub/mcp-crawl4ai-rag)
docker-compose up --build
```

## Script Permissions

### Making Scripts Executable (WSL/Linux)
```bash
# Make all scripts executable
chmod +x scripts/*.sh

# Or individually
chmod +x scripts/mcp-launcher.sh
chmod +x scripts/setup-mcp-config.sh
```

### PowerShell Execution Policy (Windows)
```powershell
# Check current policy
Get-ExecutionPolicy

# Set to allow local scripts (if needed)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Related Documentation

- **Cross-Platform Setup**: [docs/guides/CROSS_PLATFORM_MCP_SETUP.md](../docs/guides/CROSS_PLATFORM_MCP_SETUP.md)
- **Docker Setup**: [docs/DOCKER_SETUP.md](../docs/DOCKER_SETUP.md)
- **Troubleshooting**: [docs/guides/TROUBLESHOOTING.md](../docs/guides/TROUBLESHOOTING.md)

---

**Last Updated**: October 28, 2025
**Maintained By**: MCP Crawl4AI RAG Team
