# 🤖 AI Agent Command Center

This is a full-stack demo of an autonomous AI agent using LangGraph, Ollama, and Flask. You provide a high-level goal, and the AI agent (running locally) will clarify the goal, create a step-by-step plan, execute it, and synthesize a final report.

The UI is a "glassmorphism" command center that streams the agent's progress in real-time.

---

## ✨ Features

- **Autonomous Planning:** Agent autonomously clarifies goals, plans, and executes.
- **Real-Time UI:** Live log streaming and pipeline visualization via WebSockets.
- **Local First:** Runs entirely on your local machine using Ollama.
- **Automated Setup:** Simple setup scripts to install all dependencies.
- **Persistent Data:** Uses a SQLite database for missions and ideas with full CRUD support.

## 🛠️ Tech Stack

- **Backend:** Flask, LangGraph, LangChain, Flask-SocketIO, SQLite
- **Frontend:** HTML, Bootstrap 5, JavaScript
- **LLM:** Ollama (`llama3.2:1b` by default)

---

## 🚀 Getting Started

Follow these steps to get the project running. The setup scripts will handle installing all necessary software and dependencies.

### 1. Run the Setup Script

Open your terminal, navigate to the project root, and run the appropriate script for your OS.

**On Windows (Command Prompt or PowerShell):**

```bat
REM This will install Python and Ollama (via winget), pull the LLM model,
REM create a virtual environment, and install Python packages.
setup.bat
```

**On Linux or macOS:**

```bash
# First, make the script executable
chmod +x setup.sh

# This will install Ollama, pull the LLM model, create a virtual
# environment, and install Python packages.
./setup.sh
```

### 2. Run the Application

Once setup is complete, use the start script to launch the application.

**On Windows (Command Prompt or PowerShell):**

```bat
start.bat
