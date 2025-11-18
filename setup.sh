#!/bin/bash
# This script automates the setup for the AI Planner project on Linux and macOS.
#
# To run this script:
# 1. Open your terminal.
# 2. Navigate to the project root directory.
# 3. Make the script executable: chmod +x setup.sh
# 4. Run the script: ./setup.sh

echo "--- AI Planner Setup (Linux/macOS) ---"

# Check if python3 is available
if ! command -v python3 &> /dev/null
then
    echo "Python3 not found. Attempting to install..."
    if command -v apt-get &> /dev/null; then
        echo "Found 'apt-get'. Running 'sudo apt-get update && sudo apt-get install -y python3'."
        sudo apt-get update && sudo apt-get install -y python3
    elif command -v brew &> /dev/null; then
        echo "Found 'brew'. Running 'brew install python'."
        brew install python
    else
        echo "❌ ERROR: Could not find a supported package manager (apt-get or brew) to install Python."
        echo "Please install Python 3.8+ manually and re-run this script."
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        echo "❌ ERROR: Python installation failed. Please install Python 3.8+ manually."
        exit 1
    fi
    echo "✓ Python installed successfully."
fi

# Check for Ollama
echo "Checking for Ollama..."
if ! command -v ollama &> /dev/null
then
    echo "Ollama not found. Attempting to install..."
    # Check for curl, which is required for the installation script
    if ! command -v curl &> /dev/null
    then
        echo "❌ ERROR: 'curl' is required to install Ollama but it's not installed." >&2
        echo "Please install curl (e.g., 'sudo apt install curl' or 'brew install curl') and re-run this script." >&2
        exit 1
    fi

    # Run the official Ollama installation script
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✓ Ollama installed."
else
    echo "✓ Ollama is already installed."
fi

# Check for and pull the LLM model
MODEL_NAME="llama3.2:1b"
echo "Checking for Ollama model: $MODEL_NAME..."
if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "Model not found. Pulling '$MODEL_NAME' from Ollama..."
    echo "(This may take several minutes and requires an internet connection)"
    ollama pull "$MODEL_NAME"
else
    echo "✓ Model '$MODEL_NAME' is already installed."
fi

# 1. Create a virtual environment
echo "1. Creating Python virtual environment in './.venv'..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to create virtual environment."
    exit 1
fi

# 2. Upgrade Pip & Install dependencies
echo "2. Upgrading Pip and installing dependencies..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r backend/requirements.txt

# 3. Delete old database
echo "3. Deleting old database (if it exists)..."
rm -f ./instance/planner.sqlite

# 3. Initialize the database
echo "3. Initializing the database..."
export FLASK_APP="backend:create_app"
./.venv/bin/flask init-db
unset FLASK_APP

echo "✅ Setup complete!"
echo "You can now start the application by running: ./start.sh"