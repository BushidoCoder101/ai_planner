@echo off
:: This script automates the setup for the AI Planner project on Windows.
::
:: To run this script:
:: 1. Open Command Prompt or PowerShell.
:: 2. Navigate to the project root directory.
:: 3. Run the command: setup.bat

echo --- AI Planner Setup (Windows) ---

:: Check for winget
echo Checking for Windows Package Manager (winget)...
where winget >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: winget is not available.
    echo Please install 'App Installer' from the Microsoft Store to use this automated script, then re-run.
    echo https://apps.microsoft.com/store/detail/app-installer/9NBLGGH4NNS1
    goto :eof
)
echo ✓ winget found.

:: Check for Python
echo Checking for Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Installing with winget...
    winget install --id Python.Python.3 -e --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Python via winget.
        goto :eof
    )
    echo ✓ Python installed successfully.
) else (
    echo ✓ Python is already installed.
)

:: Check for Ollama
echo Checking for Ollama...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo Ollama not found. Installing with winget...
    winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Ollama via winget.
        goto :eof
    )
    echo ✓ Ollama installed successfully.
) else (
    echo ✓ Ollama is already installed.
)

:: Check for and pull the LLM model
set "MODEL_NAME=llama3.2:1b"
echo Checking for Ollama model: %MODEL_NAME%...
ollama list | findstr /C:"%MODEL_NAME%" >nul
if %errorlevel% neq 0 (
    echo Model not found. Pulling '%MODEL_NAME%' from Ollama...
    echo (This may take several minutes and requires an internet connection)
    ollama pull %MODEL_NAME%
) else (
    echo ✓ Model '%MODEL_NAME%' is already installed.
)

:: 1. Create a virtual environment
echo 1. Creating Python virtual environment in '.\.venv'...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment. Please ensure Python is installed and in your PATH.
    goto :eof
)

:: 2. Upgrade Pip and install dependencies
echo 2. Upgrading Pip and installing dependencies...
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

:: 3. Delete old database and initialize
echo 3. Deleting old database (if it exists)...
if exist .\\instance\\planner.sqlite del .\\instance\\planner.sqlite
echo 4. Initializing the database...
set FLASK_APP=backend:create_app
.\.venv\Scripts\flask.exe init-db

echo.
echo Setup complete!
echo You can now start the application by running: start.bat