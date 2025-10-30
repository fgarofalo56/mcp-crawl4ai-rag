# Cross-platform MCP server launcher for Windows PowerShell
# Usage: .\scripts\mcp-launcher.ps1

$ErrorActionPreference = "Stop"

# Get project root (parent of scripts directory)
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Platform: Windows PowerShell" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot" -ForegroundColor Cyan

# Activate virtual environment
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & $VenvActivate
} else {
    Write-Warning "Virtual environment not found at $VenvActivate"
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow

    Push-Location $ProjectRoot
    uv venv
    & ".venv\Scripts\Activate.ps1"
    uv pip install -e ".[dev]"
    Pop-Location
}

# Change to project root and run server
Push-Location $ProjectRoot
python run_mcp.py $args
Pop-Location
