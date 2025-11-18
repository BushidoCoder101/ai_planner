#!/bin/bash
# This script starts the AI Planner backend server.
# It assumes dependencies have already been installed by running setup.sh.
#
# To run this script:
# 1. Open your terminal.
# 2. Navigate to the project root directory.
# 3. Make the script executable: chmod +x start.sh
# 4. Run the script: ./start.sh

echo "--- Starting AI Planner ---"

VENV_PYTHON="./.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ ERROR: Virtual environment not found at './.venv'."
    echo "Please run './setup.sh' first to install dependencies."
    exit 1
fi

"$VENV_PYTHON" run.py