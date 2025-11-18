# c:/Users/dbmar/Downloads/ai_planner/backend/app.py
from flask import Flask, jsonify
import os
import webbrowser
import threading
from flask_socketio import SocketIO
from flask_cors import CORS

# --- 1. App Initialization ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Use eventlet or gevent for production, but the development server works for this setup.
socketio = SocketIO(app, cors_allowed_origins="*")

# --- 2. Import and Register Controllers ---
# Import the mission controller and register its routes.
# Use a flexible import pattern so the module works both when run as
# a script (python backend/app.py) and when run as a package
# (python -m backend.app).
try:
    # If running as a package
    from . import mission_controller as _mission_controller
except Exception:
    # If running as a script from the backend/ directory
    import mission_controller as _mission_controller

# mission_controller exposes registration functions. Call them to
# attach routes and socket events to the app/socketio instances.
_mission_controller.register_mission_routes(app, socketio)
_mission_controller.register_idea_routes(app)

# --- 3. Health Check Endpoint ---
@app.route('/api/health', methods=['GET'])
def health_check():
    """Basic health check to confirm the server is running."""
    return jsonify({
        "status": "healthy",
        "version": "3.0.0-mvc"
    })

# --- 4. Run Application ---
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 AI Planner Backend Server (MVC)")
    print("=" * 60)
    print(f"Port: 5000")
    print("Status: ✓ Ready")
    print("=" * 60 + "\n")
    # Use socketio.run to start both the Flask app and the WebSocket server
    # Try to open the frontend HTML in the user's default browser shortly
    # after the server starts. Use a small delay so the server is listening.
    def _open_frontend():
        # Construct the local file URL for the frontend HTML
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        front_path = os.path.join(root, 'frontend', 'ai_planner.html')
        if os.path.exists(front_path):
            url = 'file://' + front_path.replace('\\', '/')
            try:
                webbrowser.open_new_tab(url)
                print(f"Opening frontend: {url}")
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
        else:
            print(f"Frontend file not found at {front_path}")

    # Schedule the browser open to run after a short delay in a background thread
    threading.Timer(1.0, _open_frontend).start()

    # If any frontend pages are already open and connected, ask them to reload.
    # Start a small background task that waits briefly for clients to connect,
    # then emits a 'reload' event which the frontend listens for.
    def _emit_reload():
        import time as _t
        _t.sleep(1.5)
        try:
            socketio.emit('reload')
            print('Emitted reload event to connected clients')
        except Exception as _e:
            print(f'Could not emit reload event: {_e}')

    try:
        socketio.start_background_task(_emit_reload)
    except Exception:
        # If start_background_task isn't available in the current async mode,
        # fall back to a plain thread.
        threading.Thread(target=_emit_reload, daemon=True).start()

    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)