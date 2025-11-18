# c:/Users/dbmar/Downloads/ai_planner/backend/api.py
from flask import Blueprint, jsonify, request
from . import db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/health', methods=['GET'])
def health_check():
    """Health Check
    Confirms that the backend server is running.
    ---
    tags:
      - General
    responses:
      200:
        description: Server is healthy.
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            version:
              type: string
              example: 4.0.0-final
    """
    return jsonify({"status": "healthy", "version": "4.0.0-final"})

@bp.route('/missions', methods=['GET'])
def get_missions():
    """Get All Missions
    Retrieves a list of all missions from the database.
    ---
    tags:
      - Missions
    responses:
      200:
        description: A list of mission objects.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              goal:
                type: string
              status:
                type: string
    """
    missions = db.get_all_missions()
    return jsonify([dict(m) for m in missions])

@bp.route('/missions/<mission_id>', methods=['DELETE'])
def delete_mission(mission_id):
    """Delete a Mission
    Deletes a specific mission from the database by its ID.
    ---
    tags:
      - Missions
    parameters:
      - name: mission_id
        in: path
        type: string
        required: true
        description: The ID of the mission to delete.
    responses:
      200:
        description: Mission was successfully deleted.
    """
    db.delete_mission(mission_id)
    return jsonify({"status": "deleted", "id": mission_id}), 200

@bp.route('/ideas', methods=['GET'])
def get_ideas():
    """Get All Ideas
    Retrieves a list of all saved ideas from the database.
    ---
    tags:
      - Ideas
    responses:
      200:
        description: A list of idea objects.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              goal:
                type: string
    """
    ideas = db.get_ideas()
    return jsonify([dict(row) for row in ideas])

@bp.route('/ideas', methods=['POST'])
def create_idea():
    """Create a New Idea
    Adds a new idea to the database.
    ---
    tags:
      - Ideas
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            goal:
              type: string
              description: The text of the new idea.
              example: "Develop a new feature for the UI"
    responses:
      201:
        description: The newly created idea object.
    """
    data = request.get_json()
    if not data or not data.get('goal'):
        return jsonify({"error": "Goal not provided"}), 400
    new_idea = db.create_idea(data['goal'])
    return jsonify(dict(new_idea)), 201

@bp.route('/ideas/<int:idea_id>', methods=['PUT'])
def update_idea(idea_id):
    """Update an Idea
    Updates the text of an existing idea by its ID.
    ---
    tags:
      - Ideas
    parameters:
      - name: idea_id
        in: path
        type: integer
        required: true
        description: The ID of the idea to update.
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            goal:
              type: string
              description: The updated text for the idea.
    responses:
      200:
        description: The updated idea object.
      404:
        description: Idea not found.
    """
    data = request.get_json()
    idea = db.get_idea(idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404
    updated_idea = db.update_idea(idea_id, data.get('goal'))
    return jsonify(dict(updated_idea)), 200

@bp.route('/ideas/<int:idea_id>', methods=['DELETE'])
def delete_idea(idea_id):
    """Delete an Idea
    Deletes an idea from the database by its ID.
    ---
    tags:
      - Ideas
    parameters:
      - name: idea_id
        in: path
        type: integer
        required: true
        description: The ID of the idea to delete.
    responses:
      200:
        description: Idea was successfully deleted.
      404:
        description: Idea not found.
    """
    idea = db.get_idea(idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404
    db.delete_idea(idea_id)
    return jsonify({"status": "deleted", "id": idea_id}), 200