"""
Entry point for running the Mamdani Tracker application.

This script can be run directly:
    python run.py

Or the package can be run as a module:
    python -m mamdani_tracker.app
"""
import sys
import os

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mamdani_tracker.app import create_app, socketio

if __name__ == '__main__':
    print("Starting Mamdani Tracker...")
    print("Access the dashboard at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app = create_app()
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
