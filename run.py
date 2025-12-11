#!/usr/bin/env python
"""
Run script for Render deployment.
Ensures correct working directory and starts the Flask server.
"""

import os
import sys

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Change to src directory
os.chdir(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the Flask app
from web_server import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
