# c:/Users/dbmar/Downloads/ai_planner/backend/app.py
import os
import webbrowser
import threading
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

socketio = SocketIO(cors_allowed_origins="*")

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'planner.sqlite'),
    )
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions and register blueprints
    from . import db
    db.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    socketio.init_app(app)
    return app