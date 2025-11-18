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

    # This function will run only once, in the reloader's child process
    def open_browser_tabs():
        # Open the main frontend UI
        root = os.path.abspath(os.path.dirname(__file__))
        front_path = os.path.join(root, 'frontend', 'ai_planner.html')
        if os.path.exists(front_path):
            try:
                webbrowser.open_new_tab('file://' + front_path.replace('\\', '/'))
            except Exception as e:
                print(f"Could not open frontend automatically: {e}")
        
        # Open the Swagger API docs
        def _open_swagger():
            try:
                webbrowser.open_new_tab("http://127.0.0.1:5000/apidocs")
            except Exception as e:
                print(f"Could not open Swagger UI automatically: {e}")
        
        # Use a small delay for the second tab
        threading.Timer(0.5, _open_swagger).start()

    # When using debug mode, Flask's reloader runs the script twice.
    # This check ensures the browser only opens in the child process.
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser_tabs).start()

    print(f"Port: 5000 | Status: ✓ Ready")
    print("=" * 60 + "\n")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)