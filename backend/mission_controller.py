# c:/Users/dbmar/Downloads/ai_planner/backend/controllers/mission_controller.py
from flask import request, jsonify

# In-memory store for missions and ideas for simplicity.
# In a real app, this would be a database.
missions = {}
previous_ideas = [
    {"goal": "Analyze top 3 competitors in the AI chatbot market, focusing on features and pricing."},
    {"goal": "Create a marketing plan for a new productivity app targeting students."},
    {"goal": "Generate a technical blog post about the benefits of serverless architecture."},
]

def register_mission_routes(app, socketio):
    """
    Registers routes and socket events for missions.
    This is the 'Controller' in our MVC architecture.
    """

    @app.route('/api/missions', methods=['POST'])
    def start_mission():
        """
        API endpoint to start a new AI mission.
        Expects a JSON body with a 'goal'.
        """
        data = request.get_json()
        if not data or not data.get('goal'):
            return jsonify({"error": "Goal not provided"}), 400

        goal = data['goal']

        # 1. Create the Agent Service (which contains the business logic)
        # Import AgentService here to avoid heavy/optional imports at module
        # import time (this also avoids import errors if optional deps are
        # missing until a mission is actually started).
        try:
            from .agent_service import AgentService
        except Exception:
            from agent_service import AgentService

        agent_service = AgentService(goal, socketio)
        missions[agent_service.mission.id] = agent_service

        # 2. Run the mission in a background thread to not block the request
        socketio.start_background_task(agent_service.run)

        # 3. Return an immediate response to the client
        return jsonify(agent_service.mission.to_dict()), 202  # 202 Accepted

    @socketio.on('connect')
    def handle_connect():
        """Handles a new client connecting via WebSocket."""
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handles a client disconnecting."""
        print('Client disconnected')

def register_idea_routes(app):
    """Registers the route for fetching previous ideas."""
    @app.route('/api/ideas', methods=['GET'])
    def get_ideas():
        """API endpoint to get a list of previous ideas."""
        return jsonify(previous_ideas)