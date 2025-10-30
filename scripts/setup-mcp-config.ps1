# Setup MCP configuration for current platform
# Usage: .\scripts\setup-mcp-config.ps1 [-Platform windows|wsl]

param(
    [Parameter()]
    [ValidateSet("windows", "wsl")]
    [string]$Platform = "windows"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Setting up MCP configuration for platform: $Platform" -ForegroundColor Cyan

$SourceConfig = Join-Path $ProjectRoot ".mcp.json.$Platform"
$TargetConfig = Join-Path $ProjectRoot ".mcp.json"

if (Test-Path $SourceConfig) {
    Copy-Item $SourceConfig $TargetConfig -Force
    Write-Host "✓ Copied $SourceConfig to $TargetConfig" -ForegroundColor Green
} else {
    Write-Error "Platform configuration not found: $SourceConfig"
    exit 1
}

Write-Host "✓ MCP configuration setup complete for $Platform" -ForegroundColor Green
Write-Host ""
Write-Host "To verify, run:" -ForegroundColor Yellow
Write-Host "  Get-Content .mcp.json" -ForegroundColor White
