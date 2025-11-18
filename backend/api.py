# c:/Users/dbmar/Downloads/ai_planner/backend/api.py
from flask import Blueprint, jsonify, request
from . import db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "4.0.0-final"})

@bp.route('/missions', methods=['GET'])
def get_missions():
    missions = db.get_all_missions()
    return jsonify([dict(m) for m in missions])

@bp.route('/missions/<mission_id>', methods=['DELETE'])
def delete_mission(mission_id):
    db.delete_mission(mission_id)
    return jsonify({"status": "deleted", "id": mission_id}), 200

@bp.route('/ideas', methods=['GET'])
def get_ideas():
    ideas = db.get_ideas()
    return jsonify([dict(row) for row in ideas])

@bp.route('/ideas', methods=['POST'])
def create_idea():
    data = request.get_json()
    if not data or not data.get('goal'):
        return jsonify({"error": "Goal not provided"}), 400
    new_idea = db.create_idea(data['goal'])
    return jsonify(dict(new_idea)), 201

@bp.route('/ideas/<int:idea_id>', methods=['PUT'])
def update_idea(idea_id):
    data = request.get_json()
    idea = db.get_idea(idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404
    updated_idea = db.update_idea(idea_id, data.get('goal'))
    return jsonify(dict(updated_idea)), 200

@bp.route('/ideas/<int:idea_id>', methods=['DELETE'])
def delete_idea(idea_id):
    idea = db.get_idea(idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404
    db.delete_idea(idea_id)
    return jsonify({"status": "deleted", "id": idea_id}), 200