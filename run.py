#!/usr/bin/env python3
"""
BiasDetector - Run Script

This script provides a convenient way to run the BiasDetector application
in different modes.

Usage:
    python run.py [--dev] [--port PORT]

Options:
    --dev       Run in development mode with hot reloading
    --port PORT Set the port to run on (default: 5000)
"""

import os
import sys
import argparse
from main import app

def main():
    parser = argparse.ArgumentParser(description='Run BiasDetector')
    parser.add_argument('--dev', action='store_true', help='Run in development mode with hot reloading')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    args = parser.parse_args()
    
    port = args.port
    host = '0.0.0.0'  # Bind to all interfaces
    
    if args.dev:
        # Development mode with auto-reloading
        print(f"Starting BiasDetector in development mode on http://{host}:{port}")
        app.run(host=host, port=port, debug=True)
    else:
        # Production mode using gunicorn if available
        try:
            from gunicorn.app.base import BaseApplication
            
            class GunicornApplication(BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()
                
                def load_config(self):
                    for key, value in self.options.items():
                        if key in self.cfg.settings and value is not None:
                            self.cfg.set(key.lower(), value)
                
                def load(self):
                    return self.application
            
            options = {
                'bind': f'{host}:{port}',
                'workers': 2,
                'timeout': 60,
                'reload': False
            }
            
            print(f"Starting BiasDetector in production mode on http://{host}:{port}")
            GunicornApplication(app, options).run()
            
        except ImportError:
            # Fall back to Flask's built-in server if gunicorn is not available
            print(f"Gunicorn not found. Starting BiasDetector with Flask's built-in server on http://{host}:{port}")
            print(f"Warning: This is not recommended for production use")
            app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    main()