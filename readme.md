AI Agent Command Center



This is a full-stack demo of an autonomous AI agent using LangGraph, Ollama, and Flask.



You provide a goal, and the AI agent (running locally via Ollama) will:



Clarify the goal.



Create a step-by-step plan.



Execute the plan (calling mock tools).



Synthesize a final report.



The UI is a "glassmorphism" command center that streams the agent's thoughts and visualizes its progress in real-time.



The Stack



Backend: Flask, LangGraph, LangChain, Ollama



Frontend: HTML, Bootstrap 5, JavaScript



LLM: Ollama (requires llama3 model)


# AI Planner — Command Center

This is a local demo: a Flask + Socket.IO backend that runs an AI "mission" pipeline and a static frontend dashboard in `frontend/ai_planner.html`.

Key features
- Clarify user goal → create plan → execute steps → synthesize report
- Live logs and status via Socket.IO
- Auto-open frontend on backend start and request client reloads
- Uses Ollama (LLM) by default with model `llama3.2:1b`

## Quick start (Windows PowerShell)

1) Create and activate a virtual environment, install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

2) Start the backend (preferred, runs as a package):

```powershell
python -m backend.app
```

This will start the server on http://127.0.0.1:5000, attempt to open `frontend/ai_planner.html` in your default browser, and emit a `reload` event to connected clients so already-open pages refresh.

Alternative (less preferred):

```powershell
python backend\app.py
```

3) If the frontend didn't open automatically, open `frontend/ai_planner.html` in your browser. The page connects back to the backend at http://localhost:5000 for APIs and Socket.IO.

## LLM / Ollama

- The code uses `llama3.2:1b` by default (see `backend/agent_service.py` CONFIG). Ensure your Ollama server is running and the model name matches.
- If Ollama returns a different output format, the code includes parsing and normalization logic to recover a usable clarified goal/plan/report.

## Recent fixes & behavior notes

- Fixed relative-import issues so running the backend as a package works (avoids "attempted relative import with no known parent package").
- Auto-opens the frontend file and emits a `reload` event so already-open clients refresh automatically.
- Normalizes graph state and reconstructs `Mission` objects if the graph runtime returns plain dicts (fixes errors like `'dict' object has no attribute 'mission'`).
- Switched from ChatPromptTemplate variable binding to direct `llm.invoke(prompt_text)` plus JSON-safe parsing to avoid LangChain template variable errors when model output contains braces.

## Troubleshooting

- ImportError / relative import errors: run with `python -m backend.app` from the project root.
- Missing packages: `python -m pip install -r backend\requirements.txt`.
- Ollama/model errors: check that your Ollama server is running and the model `llama3.2:1b` (or your chosen model) is installed and available.
- Frontend not reloading: the backend emits a `reload` Socket.IO event on startup; ensure your browser allows automatic reloads or refresh manually.

## Developer notes

- To disable auto-open, comment out or remove the `_open_frontend` timer call in `backend/app.py`.
- To serve the frontend from Flask instead of opening `file://` URLs, I can add a static route and open `http://localhost:5000/`.

## Project layout

- `backend/` — Flask app, agent logic, requirements
- `frontend/` — static HTML/JS/CSS dashboard

---

If you'd like, I can:
- Serve the frontend from Flask and open `http://localhost:5000/` instead of a file URL
- Add unit tests for state normalization and prompt parsing
- Add a small CLI flag to toggle auto-open behavior

Tell me which you'd like next.

