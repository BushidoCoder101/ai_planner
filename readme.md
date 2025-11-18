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



How to Run



1\. Prerequisites



Python 3.9+



Ollama installed and running.



2\. Install \& Run Backend



Install Ollama Model:



ollama pull llama3





Install Python Dependencies:



\# It's recommended to use a virtual environment

python -m venv venv

source venv/bin/activate  # On Windows: venv\\Scripts\\activate

pip install -r requirements.txt





Start the Server:



python app.py





(The server will run on http://127.0.0.1:5000)



3\. Run the Frontend



Open the index.html file in your web browser.



Enter a goal and click "Execute Plan".

