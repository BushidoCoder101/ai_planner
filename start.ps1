# This script starts the AI Planner backend server.
# It assumes dependencies have already been installed by running setup.ps1.
#
# To run this script:
# 1. Open PowerShell.
# 2. Navigate to the project root directory.
# 3. Run the command: .\start.ps1

Write-Host "--- Starting AI Planner ---" -ForegroundColor Green

# 1. Check for virtual environment
$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "❌ ERROR: Virtual environment not found at '.\.venv'." -ForegroundColor Red
    Write-Host "Please run '.\setup.ps1' first to install dependencies." -ForegroundColor Yellow
    exit 1
}

# 2. Run the application as a module
& $venvPython -m backend.app