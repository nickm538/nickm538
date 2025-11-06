#!/usr/bin/env python3
"""
Entrypoint script to run the Mamdani Tracker application.

Usage:
    python run.py
    
Or run as a module:
    python -m mamdani_tracker.app
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    from mamdani_tracker.app import create_app, socketio
    
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Mamdani Tracker...")
    print(f"Local access: http://localhost:{port}")
    print(f"Network access: http://<your-ip>:{port}")
    print(f"For iPhone testing: Find your local IP and use http://<your-ip>:{port}")
    print(f"Or use ngrok: ngrok http {port}")
    
    # Run with SocketIO
    socketio.run(app, host=host, port=port, debug=debug)
