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
    echo "❌ ERROR: python3 could not be found."
    echo "Please install Python 3.8+ from https://www.python.org/downloads/ or using your system's package manager."
    echo "Example for Debian/Ubuntu: sudo apt update && sudo apt install python3"
    exit 1
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

echo "✅ Setup complete!"
echo "Next steps: Activate the environment by running: source .venv/bin/activate"