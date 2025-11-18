# This script automates the setup for the AI Planner project on Windows using PowerShell.
#
# To run this script:
# 1. Open PowerShell.
# 2. Navigate to the project root directory.
# 3. Run the command: .\setup.ps1
#
# If you get an error about execution policies, you may need to run this command first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

Write-Host "--- AI Planner Setup (Windows) ---" -ForegroundColor Green

# Check for winget
Write-Host "Checking for Windows Package Manager (winget)..."
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: winget is not available." -ForegroundColor Red
    Write-Host "Please install 'App Installer' from the Microsoft Store to use this automated script, then re-run." -ForegroundColor Yellow
    Write-Host "https://apps.microsoft.com/store/detail/app-installer/9NBLGGH4NNS1" -ForegroundColor Cyan
    exit 1
}
Write-Host "✓ winget found."

# Check for Python
Write-Host "Checking for Python..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Installing with winget..."
    winget install --id Python.Python.3 -e --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to install Python via winget." -ForegroundColor Red; exit 1
    }
    Write-Host "✓ Python installed successfully."
} else {
    Write-Host "✓ Python is already installed."
}

# Check for Ollama
Write-Host "Checking for Ollama..."
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama not found. Installing with winget..."
    winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to install Ollama via winget." -ForegroundColor Red; exit 1
    }
    Write-Host "✓ Ollama installed successfully."
} else {
    Write-Host "✓ Ollama is already installed."
}

# Check for and pull the LLM model
$modelName = "llama3.2:1b"
Write-Host "Checking for Ollama model: $modelName..."
if (-not (ollama list | Select-String -Pattern $modelName -Quiet)) {
    Write-Host "Model not found. Pulling '$modelName' from Ollama..."
    Write-Host "(This may take several minutes and requires an internet connection)"
    ollama pull $modelName
} else {
    Write-Host "✓ Model '$modelName' is already installed."
}

# 1. Create a virtual environment
Write-Host "1. Creating Python virtual environment in '.\.venv'..."
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Failed to create virtual environment. Please ensure Python is installed and in your PATH." -ForegroundColor Red
    exit 1
}

# 2. Upgrade Pip
Write-Host "2. Upgrading Pip..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# 3. Install dependencies
Write-Host "3. Installing dependencies from 'backend\requirements.txt'..."
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "Next steps: Activate the environment by running: .\.venv\Scripts\Activate.ps1"