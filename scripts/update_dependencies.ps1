#!/usr/bin/env pwsh
# Script to update dependencies by stopping Claude Desktop, updating venv, and restarting

Write-Host "🔧 Updating MCP Server Dependencies" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop Claude Desktop
Write-Host "📛 Stopping Claude Desktop processes..." -ForegroundColor Yellow
$claudeProcesses = Get-Process -Name "Claude" -ErrorAction SilentlyContinue
if ($claudeProcesses) {
    $claudeProcesses | Stop-Process -Force
    Write-Host "✅ Stopped $($claudeProcesses.Count) Claude Desktop process(es)" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "ℹ️  Claude Desktop is not running" -ForegroundColor Gray
}

# Step 2: Wait for file locks to release
Write-Host "⏳ Waiting for file locks to release..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 3: Update dependencies
Write-Host "📦 Syncing dependencies with websockets v13.x..." -ForegroundColor Yellow
try {
    uv sync
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies updated successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to update dependencies (Exit code: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error during dependency update: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Restart Claude Desktop
Write-Host ""
Write-Host "🚀 Restarting Claude Desktop..." -ForegroundColor Yellow
$claudePath = "C:\Users\frgarofa\AppData\Local\AnthropicClaude\app-0.13.37\claude.exe"

if (Test-Path $claudePath) {
    Start-Process $claudePath
    Write-Host "✅ Claude Desktop started!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Could not find Claude Desktop at: $claudePath" -ForegroundColor Yellow
    Write-Host "   Please start Claude Desktop manually" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✨ Update complete! The websockets deprecation warnings should now be gone." -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Wait for Claude Desktop to fully load" -ForegroundColor Gray
Write-Host "  2. Check the MCP server logs - deprecation warnings should be gone" -ForegroundColor Gray
Write-Host "  3. Test your MCP tools to ensure everything works" -ForegroundColor Gray
