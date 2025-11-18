# This is the main entry point to run the application.
import os
import threading
import webbrowser
from backend.app import create_app, socketio
import eventlet

# Apply eventlet's monkey patching for cooperative multi-threading.
eventlet.monkey_patch()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 AI Planner Backend Server")
    print("=" * 60)

    # Create the Flask app instance using the factory
    app = create_app()

    def open_browser_tabs():
        """Opens the frontend and Swagger UI in new browser tabs."""
        print("Opening browser tabs...")
        webbrowser.open_new_tab("http://127.0.0.1:5000/")
        # Add a small delay for the second tab to avoid issues in some browsers
        threading.Timer(0.5, lambda: webbrowser.open_new_tab("http://127.0.0.1:5000/apidocs")).start()

    def run_server():
        """Runs the SocketIO server."""
        # Use eventlet to run the server for stable WebSocket support.
        # This is the recommended way for Flask-SocketIO.
        print(f"Port: 5000 | Status: ✓ Ready")
        print("=" * 60 + "\n")
        socketio.run(app, host='0.0.0.0', port=5000)
    
    # 1. Start the server in a non-blocking way using eventlet's spawn.
    #    This is the correct way to run a background task with eventlet.
    server_gt = eventlet.spawn(run_server)
    
    # 2. Wait a moment for the server to initialize before opening the browser.
    eventlet.sleep(2.0)
    open_browser_tabs()
    
    # 3. Keep the main script alive. The server is running in a greenthread.
    try:
        server_gt.wait()
    except KeyboardInterrupt:
        print("\nShutting down server...")