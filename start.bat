@echo off
:: This script starts the AI Planner backend server.
:: It assumes dependencies have already been installed by running setup.bat.
::
:: To run this script:
:: 1. Open Command Prompt or PowerShell.
:: 2. Navigate to the project root directory.
:: 3. Run the command: start.bat

echo --- Starting AI Planner ---

if not exist .\.venv\Scripts\python.exe (
    echo ERROR: Virtual environment not found at '.\.venv'.
    echo Please run 'setup.bat' first to install dependencies.
    goto :eof
)

.\.venv\Scripts\python.exe run.py