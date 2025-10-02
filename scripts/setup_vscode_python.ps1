# VS Code Extensions and Python Setup Script
# Run this script in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VS Code Extensions & Python Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Install VS Code Extensions
Write-Host "`nStep 1: Installing VS Code Extensions..." -ForegroundColor Yellow

$extensions = @(
    "ms-python.pylint",
    "ms-python.flake8", 
    "ms-python.mypy-type-checker",
    "ms-python.black-formatter",
    "ms-python.isort",
    "usernamehw.errorlens"
)

foreach ($ext in $extensions) {
    Write-Host "Installing $ext..." -ForegroundColor Green
    code-insiders --install-extension $ext --force
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $ext installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install $ext" -ForegroundColor Red
    }
}

# Step 2: Download and Install Python 3.12
Write-Host "`nStep 2: Setting up Python 3.12..." -ForegroundColor Yellow

$pythonVersion = "3.12.8"
$pythonUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
$pythonInstaller = "$env:TEMP\python-$pythonVersion-amd64.exe"

# Check if Python 3.12 is already installed
$python312Path = "C:\Program Files\Python312\python.exe"
if (Test-Path $python312Path) {
    Write-Host "Python 3.12 is already installed at $python312Path" -ForegroundColor Green
} else {
    Write-Host "Downloading Python $pythonVersion..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    
    Write-Host "Installing Python $pythonVersion..." -ForegroundColor Cyan
    Write-Host "Please follow the installer prompts. Make sure to:" -ForegroundColor Yellow
    Write-Host "  1. Check 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "  2. Choose 'Install for all users'" -ForegroundColor Yellow
    Write-Host "  3. Install to 'C:\Program Files\Python312'" -ForegroundColor Yellow
    
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "DefaultAllUsersTargetDir=C:\Program Files\Python312" -Wait
    
    # Clean up installer
    Remove-Item $pythonInstaller -Force
    Write-Host "✓ Python $pythonVersion installation complete" -ForegroundColor Green
}

# Step 3: Set up Environment Variables for API Tokens
Write-Host "`nStep 3: Setting up Environment Variables..." -ForegroundColor Yellow

# Function to set environment variable
function Set-EnvironmentVariable {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Scope = "User"
    )
    
    [Environment]::SetEnvironmentVariable($Name, $Value, $Scope)
    Write-Host "✓ Set $Name environment variable" -ForegroundColor Green
}

# Check if environment variables already exist
$localToken = [Environment]::GetEnvironmentVariable("LOCAL_API_TOKEN", "User")
$stagingToken = [Environment]::GetEnvironmentVariable("STAGING_API_TOKEN", "User")

if (-not $localToken) {
    $inputToken = Read-Host "Enter your LOCAL_API_TOKEN (or press Enter to set it to 'your-local-token-here')"
    if ([string]::IsNullOrWhiteSpace($inputToken)) {
        $inputToken = "your-local-token-here"
    }
    Set-EnvironmentVariable -Name "LOCAL_API_TOKEN" -Value $inputToken
} else {
    Write-Host "LOCAL_API_TOKEN already exists" -ForegroundColor Green
}

if (-not $stagingToken) {
    $inputToken = Read-Host "Enter your STAGING_API_TOKEN (or press Enter to set it to 'your-staging-token-here')"
    if ([string]::IsNullOrWhiteSpace($inputToken)) {
        $inputToken = "your-staging-token-here"
    }
    Set-EnvironmentVariable -Name "STAGING_API_TOKEN" -Value $inputToken
} else {
    Write-Host "STAGING_API_TOKEN already exists" -ForegroundColor Green
}

# Step 4: Update VS Code settings to use Python 3.12
Write-Host "`nStep 4: Updating VS Code settings..." -ForegroundColor Yellow

$settingsPath = "$env:APPDATA\Code - Insiders\User\settings.json"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw
    $settings = $settings -replace '"python.defaultInterpreterPath":\s*"[^"]*"', '"python.defaultInterpreterPath": "C:\\Program Files\\Python312\\python.exe"'
    Set-Content -Path $settingsPath -Value $settings
    Write-Host "✓ Updated VS Code settings to use Python 3.12" -ForegroundColor Green
} else {
    Write-Host "✗ Could not find VS Code settings file" -ForegroundColor Red
}

# Step 5: Install Python packages for development
Write-Host "`nStep 5: Installing Python development packages..." -ForegroundColor Yellow

$packages = @(
    "black",
    "pylint", 
    "flake8",
    "mypy",
    "isort",
    "pytest",
    "pytest-cov",
    "bandit"
)

# Use Python 3.12 if available, otherwise use default python
$pythonExe = if (Test-Path "C:\Program Files\Python312\python.exe") {
    "C:\Program Files\Python312\python.exe"
} else {
    "python"
}

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    & $pythonExe -m pip install --upgrade $package
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $package installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install $package" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Restart VS Code Insiders to apply all changes" -ForegroundColor White
Write-Host "2. Update your API tokens in environment variables if needed" -ForegroundColor White
Write-Host "3. Open a Python project and verify the interpreter is set to Python 3.12" -ForegroundColor White
Write-Host "`nEnvironment Variables Set:" -ForegroundColor Yellow
Write-Host "  LOCAL_API_TOKEN = $([Environment]::GetEnvironmentVariable('LOCAL_API_TOKEN', 'User'))" -ForegroundColor White
Write-Host "  STAGING_API_TOKEN = $([Environment]::GetEnvironmentVariable('STAGING_API_TOKEN', 'User'))" -ForegroundColor White

# Prompt to restart VS Code
$restart = Read-Host "`nWould you like to restart VS Code Insiders now? (y/n)"
if ($restart -eq 'y') {
    Get-Process "Code - Insiders" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Start-Process "code-insiders"
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
