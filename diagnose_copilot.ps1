# VS Code Copilot Diagnostic Script
# Run this to diagnose and fix Copilot issues

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "COPILOT DIAGNOSTIC & FIX TOOL" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check VS Code processes
Write-Host "1. Checking VS Code processes..." -ForegroundColor Yellow
$vscode = Get-Process "Code - Insiders" -ErrorAction SilentlyContinue
if ($vscode) {
    $memoryMB = [math]::Round($vscode.WorkingSet64 / 1MB, 2)
    if ($memoryMB -gt 2000) {
        Write-Host "   ⚠️ High memory usage: $memoryMB MB" -ForegroundColor Yellow
        Write-Host "   Consider restarting VS Code" -ForegroundColor Gray
    } else {
        Write-Host "   ✅ Memory usage normal: $memoryMB MB" -ForegroundColor Green
    }
}

# 2. Check network connectivity to GitHub
Write-Host ""
Write-Host "2. Testing GitHub connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://api.github.com" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ GitHub API accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Cannot reach GitHub API" -ForegroundColor Red
    Write-Host "   Check internet connection or proxy settings" -ForegroundColor Yellow
}

# 3. Check Copilot authentication
Write-Host ""
Write-Host "3. Checking GitHub authentication..." -ForegroundColor Yellow
$githubAuth = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -ErrorAction SilentlyContinue
if ($githubAuth.ProxyEnable -eq 1) {
    Write-Host "   ⚠️ Proxy detected - may affect Copilot" -ForegroundColor Yellow
    Write-Host "   Proxy: $($githubAuth.ProxyServer)" -ForegroundColor Gray
}

# 4. Clear VS Code cache (optional)
Write-Host ""
Write-Host "4. Cache management..." -ForegroundColor Yellow
$cacheDir = "$env:APPDATA\Code - Insiders\Cache"
if (Test-Path $cacheDir) {
    $cacheSize = (Get-ChildItem $cacheDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "   Cache size: $([math]::Round($cacheSize, 2)) MB" -ForegroundColor Gray
    
    if ($cacheSize -gt 500) {
        Write-Host "   ⚠️ Large cache detected" -ForegroundColor Yellow
        $clear = Read-Host "   Clear cache? (y/n)"
        if ($clear -eq 'y') {
            Remove-Item "$cacheDir\*" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "   ✅ Cache cleared" -ForegroundColor Green
        }
    }
}

# 5. Check extension logs
Write-Host ""
Write-Host "5. Recent Copilot errors..." -ForegroundColor Yellow
$logPath = "$env:APPDATA\Code - Insiders\logs"
if (Test-Path $logPath) {
    $recentLogs = Get-ChildItem $logPath -Filter "*.log" -Recurse | 
                  Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-1) } |
                  Select-String -Pattern "copilot.*error" -SimpleMatch
    
    if ($recentLogs) {
        Write-Host "   Found recent errors:" -ForegroundColor Red
        $recentLogs | Select-Object -First 3 | ForEach-Object {
            Write-Host "   $($_.Line)" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ✅ No recent errors found" -ForegroundColor Green
    }
}

# 6. Suggested fixes
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "RECOMMENDED ACTIONS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Quick fixes to try:" -ForegroundColor Yellow
Write-Host "1. Restart Copilot: Ctrl+Shift+P → 'GitHub Copilot: Restart'" -ForegroundColor White
Write-Host "2. Reload VS Code: Ctrl+Shift+P → 'Developer: Reload Window'" -ForegroundColor White
Write-Host "3. Check status: Click Copilot icon in status bar" -ForegroundColor White
Write-Host "4. View logs: View → Output → GitHub Copilot" -ForegroundColor White
Write-Host ""

Write-Host "If still not working:" -ForegroundColor Yellow
Write-Host "1. Sign out and back in to GitHub" -ForegroundColor White
Write-Host "2. Disable/re-enable Copilot extension" -ForegroundColor White
Write-Host "3. Check firewall/proxy settings" -ForegroundColor White
Write-Host "4. Update VS Code and Copilot extensions" -ForegroundColor White
Write-Host ""

# Option to restart VS Code
$restart = Read-Host "Restart VS Code now? (y/n)"
if ($restart -eq 'y') {
    Write-Host "Restarting VS Code..." -ForegroundColor Green
    Get-Process "Code - Insiders" | Stop-Process -Force
    Start-Sleep -Seconds 2
    Start-Process "code-insiders"
}

Write-Host ""
Write-Host "Diagnostics complete!" -ForegroundColor Green
