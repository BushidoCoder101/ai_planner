# c:/Users/dbmar/Downloads/ai_planner/backend/services/agent_service.py
import time
import json
from flask import current_app
import ast
import traceback
from typing import List, Dict, Any, Optional

# Import the Mission model using a flexible path so this file works
# both as a package module and as a standalone script import.
try:
    from .mission import Mission, MissionStatus
except Exception:
    from mission import Mission, MissionStatus
from . import db

# LangChain and LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_ollama import ChatOllama

# --- 1. Service Configuration ---
CONFIG = {
    'llm_model': 'llama3.2:1b', # Using a more general model name
    'temperature': 0.2,
}

def initialize_llm():
    """Initializes and validates the LLM connection."""
    try:
        llm = ChatOllama(model=CONFIG['llm_model'], temperature=CONFIG['temperature'], format="json")
        llm.invoke("Respond with only the word 'test'")
        print(f"✓ Connected to Ollama (model: {CONFIG['llm_model']})")
        return llm
    except Exception as e:
        print(f"✗ Failed to connect to Ollama: {e}")
        return None

llm = initialize_llm()
# Create a separate LLM instance for generating plain text reports (without JSON formatting)
report_llm = ChatOllama(model=CONFIG['llm_model'], temperature=CONFIG['temperature'])
if llm:
    print("✓ Report LLM is also ready.")

# --- 2. Tool Definitions ---
@tool
def web_search(query: str) -> str:
    """Simulates a web search for a given query."""
    print(f"🔍 TOOL: web_search(query='{query}')")
    time.sleep(1)
    return f"Search results for '{query}': Found relevant information about market trends and industry insights."

tools = [web_search]

# --- 3. Graph State Definition ---
class GraphState(dict):
    """A dictionary-based state for the graph."""
    @property
    def mission(self) -> Mission:
        return self['mission']

    @property
    def execution_results(self) -> List[Dict]:
        return self.setdefault('execution_results', [])

    @property
    def current_step_index(self) -> int:
        return self.setdefault('current_step_index', 0)


def _ensure_graph_state(state: Any, default_mission: Optional[Mission] = None) -> 'GraphState':
    """Normalize incoming state to a GraphState and ensure the 'mission'
    key is a Mission instance (the graph runtime may serialize it to a dict).

    If `default_mission` is provided and 'mission' is missing, it will be
    inserted into the state to avoid KeyError in node handlers.
    """
    # Some graph runtimes may return None; handle that gracefully by
    # creating an empty GraphState which we can populate.
    if state is None:
        state = GraphState()
    elif not isinstance(state, GraphState):
        # Wrap other mapping-like inputs in a GraphState
        try:
            state = GraphState(state)
        except Exception:
            # If state is not iterable/mapping, fall back to empty GraphState
            state = GraphState()

    # If mission is missing entirely, set it to default_mission when available.
    if 'mission' not in state and default_mission is not None:
        state['mission'] = default_mission

    mission_val = state.get('mission')
    if isinstance(mission_val, dict):
        md = mission_val
        # Reconstruct a Mission object from dict fields where possible.
        m = Mission(goal=md.get('goal', ''))
        m.id = md.get('id', m.id)
        # Try to set status if available as string
        try:
            if 'status' in md and isinstance(md['status'], str):
                m.status = MissionStatus(md['status'])
        except Exception:
            pass
        m.plan = md.get('plan', []) or []
        m.report = md.get('report', '') or ''
        m.clarified_goal = md.get('clarified_goal', '') or ''
        m.logs = md.get('logs', []) or []
        state['mission'] = m

    return state

# --- 4. Agent Service Class ---
class AgentService:
    """
    Manages the lifecycle and execution of an AI mission.
    This class encapsulates the core business logic (the AI agent).
    """
    def __init__(self, goal: str, socketio, app):
        self.mission = Mission(goal=goal)
        self.socketio = socketio
        self.app = app  # Store the app instance
        self.graph = self._build_graph()

    def _emit_log(self, message: str):
        self.socketio.emit('log', {'message': message})
        print(f"LOG: {message}")

    def _set_status(self, status: MissionStatus, node_name: str):
        self.mission.set_status(status)
        self.socketio.emit('status_update', {'status': status.value, 'node': node_name})

    def run(self):
        """Executes the full AI mission pipeline using the graph."""
        self._emit_log(f"Mission '{self.mission.id}' started for goal: '{self.mission.goal}'")

        if not llm:
            self._emit_log("🔴 FATAL: LLM (Ollama) is not available. Aborting mission.")
            self._set_status(MissionStatus.FAILED, 'handle_vague_goal')
            return

        try:
            initial_state = GraphState(mission=self.mission)
            # The graph execution is synchronous here, but runs in a background thread
            # started by the controller.
            final_state = self.graph.invoke(initial_state)

            # Normalize the returned state and ensure mission is a Mission
            # instance (the graph runtime may return plain dicts). Provide
            # the current Mission as the default so missing keys are filled.
            final_state = _ensure_graph_state(final_state, default_mission=self.mission)

            final_report = final_state['mission'].report
            if final_report:
                self.socketio.emit('final_report', {'report': final_report})

            if self.mission.status != MissionStatus.FAILED:
                self._set_status(MissionStatus.COMPLETED, 'synthesize_report')
            
            # Final state update to the DB
            with self.app.app_context():
                db.update_mission_state(self.mission)
            
            self._emit_log("✅ Mission finished.")

        except Exception as e:
            # Include full traceback for easier debugging
            tb = traceback.format_exc()
            error_message = f"An unexpected error occurred during the mission: {e}\n{tb}"
            self._emit_log(f"🔴 {error_message}")
            # Update DB with failed status
            with self.app.app_context():
                db.update_mission_state(self.mission)
            self._set_status(MissionStatus.FAILED, 'handle_vague_goal')
            print(f"ERROR: {error_message}")

    # --- Graph Nodes ---
    def _clarify_goal(self, state: GraphState) -> GraphState:
        # Normalize state and ensure mission is a Mission instance
        state = _ensure_graph_state(state, default_mission=self.mission)

        self._set_status(MissionStatus.CLARIFYING, 'clarify_goal')
        self._emit_log("🧠 Clarifying goal...")
        
        # Build a plain-text prompt and call the llm directly to avoid
        # ChatPromptTemplate variable-binding issues in some runtimes.
        system_msg = "You are a Goal Clarifier AI. Rewrite the user's goal to be more specific and actionable. Respond in JSON with a single key 'clarified_goal'."
        human_msg = f"Goal: {state.mission.goal}"
        prompt_text = system_msg + "\n\n" + human_msg

        raw = llm.invoke(prompt_text)
        # llm.invoke may return a Python dict (already parsed) or a JSON string.
        if isinstance(raw, dict):
            result = raw
        else:
            try:
                result = json.loads(str(raw))
            except Exception:
                # Fallback: wrap the raw output so callers get something sensible
                result = {'clarified_goal': str(raw)}

        # Normalize clarified_goal: models sometimes return a dict-like string.
        cg = result.get('clarified_goal', state.mission.goal)
        if isinstance(cg, dict):
            # Prefer a short description field if available
            state.mission.clarified_goal = cg.get('description', json.dumps(cg))
        elif isinstance(cg, str) and cg.strip().startswith('{'):
            # Try to parse python-style dict string safely
            try:
                parsed = ast.literal_eval(cg)
                if isinstance(parsed, dict):
                    state.mission.clarified_goal = parsed.get('description', json.dumps(parsed))
                else:
                    state.mission.clarified_goal = cg
            except Exception:
                state.mission.clarified_goal = cg
        else:
            state.mission.clarified_goal = cg
        self._emit_log(f"🎯 Goal clarified: \"{state.mission.clarified_goal}\"")
        # Persist the clarified goal
        with self.app.app_context():
            db.update_mission_state(state.mission)
        return state

    def _create_plan(self, state: GraphState) -> GraphState:
        state = _ensure_graph_state(state, default_mission=self.mission)

        self._set_status(MissionStatus.PLANNING, 'create_plan')
        self._emit_log("🗺️ Creating a step-by-step plan...")

        system_msg = "You are a Strategic Planner. Create a concise list of steps to achieve the goal. Respond in JSON with a single key 'steps' which is a list of strings."
        human_msg = f"Goal: {state.mission.clarified_goal}"
        prompt_text = system_msg + "\n\n" + human_msg

        raw = llm.invoke(prompt_text)
        if isinstance(raw, dict):
            result = raw
        else:
            try:
                result = json.loads(str(raw))
            except Exception:
                # If parsing fails, treat the raw output as a single-step plan
                result = {'steps': [str(raw)]}

        # Defensive: ensure 'steps' is a proper list of strings. Models may
        # return None, a string, or other unexpected types.
        raw_steps = result.get('steps', None)
        steps = []
        if raw_steps is None:
            steps = []
        elif isinstance(raw_steps, list):
            steps = raw_steps
        elif isinstance(raw_steps, str):
            # Try to parse JSON-like list string, then python list literal
            s = raw_steps.strip()
            if s.startswith('['):
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        steps = parsed
                    else:
                        steps = [raw_steps]
                except Exception:
                    try:
                        parsed = ast.literal_eval(s)
                        if isinstance(parsed, list):
                            steps = parsed
                        else:
                            steps = [raw_steps]
                    except Exception:
                        steps = [raw_steps]
            else:
                steps = [raw_steps]
        else:
            # Any other iterable (tuple, set) -> convert to list; otherwise single
            try:
                steps = list(raw_steps)
            except Exception:
                steps = [str(raw_steps)]

        # Normalize elements to strings for display
        steps = [str(s) for s in steps]
        state.mission.plan = steps
        # Emit the plan as structured data so the frontend can format it.
        self.socketio.emit('log', {
            'message': f"📋 Plan created ({len(steps)} steps):", 'plan': steps
        })
        # Persist the plan
        with self.app.app_context():
            db.update_mission_state(state.mission)
        return state

    def _execute_step(self, state: GraphState) -> GraphState:
        state = _ensure_graph_state(state, default_mission=self.mission)

        self._set_status(MissionStatus.EXECUTING, 'execute_step')
        step_index = state.current_step_index
        step = state.mission.plan[step_index]
        self._emit_log(f"⚙️ Executing step {step_index + 1}/{len(state.mission.plan)}: {step}")

        # Simple execution for this example: just log the step.
        # In a real scenario, this would involve tool use.
        time.sleep(1.5)
        result_log = f"Completed step: '{step}'"
        
        state.execution_results.append({'step': step, 'log': result_log})
        self._emit_log(f"✔️ Step {step_index + 1} result: {result_log}")
        state['current_step_index'] = step_index + 1
        return state

    def _synthesize_report(self, state: GraphState) -> GraphState:
        state = _ensure_graph_state(state, default_mission=self.mission)

        self._set_status(MissionStatus.REPORTING, 'synthesize_report')
        self._emit_log("📑 Synthesizing final report...")

        system_msg = "You are a Senior Analyst. Create a detailed, comprehensive, and professional report based on the provided goal and execution log. The report should be well-structured and easy to read. Use Markdown for rich formatting (e.g., # Headings, ## Sub-headings, - Bullet points, **bold** text)."
        human_msg = f"Goal: {state.mission.clarified_goal}\n\nExecution Log:\n{json.dumps(state.execution_results, indent=2)}"
        prompt_text = system_msg + "\n\n" + human_msg

        raw = report_llm.invoke(prompt_text)
        # Prefer a plain string report; if llm returned a dict, try to extract text
        if isinstance(raw, dict):
            # If the model returned structured output, try common keys
            report = raw.get('report') or raw.get('text') or json.dumps(raw)
        
        # The LLM returns a message object. We need to extract its string content.
        # The object might have a `.content` attribute (standard for LangChain messages).
        if hasattr(raw, 'content'):
            report = raw.content
        else:
            # Fallback for other types
            report = str(raw)

        state.mission.report = report
        self._emit_log("📄 Report generated.")
        # Persist the final report
        with self.app.app_context():
            db.update_mission_state(state.mission)
        return state

    # --- Graph Edges ---
    def _check_plan_execution(self, state: GraphState) -> str:
        """Conditional edge: Check if all steps are executed."""
        state = _ensure_graph_state(state, default_mission=self.mission)

        if state.current_step_index < len(state.mission.plan):
            return "execute_step"
        return "synthesize_report"

    # --- Graph Builder ---
    def _build_graph(self) -> Any:
        """Builds the LangGraph state machine."""
        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node("clarify_goal", self._clarify_goal)
        workflow.add_node("create_plan", self._create_plan)
        workflow.add_node("execute_step", self._execute_step)
        workflow.add_node("synthesize_report", self._synthesize_report)

        # Define edges
        workflow.set_entry_point("clarify_goal")
        workflow.add_edge("clarify_goal", "create_plan")
        
        workflow.add_conditional_edges(
            "create_plan",
            self._check_plan_execution,
            {
                "execute_step": "execute_step",
                "synthesize_report": "synthesize_report"
            }
        )
        workflow.add_conditional_edges(
            "execute_step",
            self._check_plan_execution,
            {
                "execute_step": "execute_step",
                "synthesize_report": "synthesize_report"
            }
        )
        workflow.add_edge("synthesize_report", END)

        return workflow.compile()