# c:/Users/dbmar/Downloads/ai_planner/backend/controllers/mission_controller.py
from flask import request, jsonify

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
        from .agent_service import AgentService
        from . import db

        agent_service = AgentService(goal, socketio, app)
        
        # Save the initial mission state to the database
        with app.app_context():
            db.create_mission(agent_service.mission)
        
        # 2. Run the mission in a background thread to not block the request
        socketio.start_background_task(agent_service.run)

        # 3. Return an immediate response to the client
        return jsonify(agent_service.mission.to_dict()), 202  # 202 Accepted