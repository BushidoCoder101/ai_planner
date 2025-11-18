# This is the main entry point to run the application.
import os
import threading
import webbrowser
from backend.app import create_app, socketio

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 AI Planner Backend Server")
    print("=" * 60)

    # Create the Flask app instance using the factory
    app = create_app()

    def _open_frontend():
        root = os.path.abspath(os.path.dirname(__file__))
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

    threading.Timer(1.0, _open_frontend).start()

    print(f"Port: 5000 | Status: ✓ Ready")
    print("=" * 60 + "\n")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)