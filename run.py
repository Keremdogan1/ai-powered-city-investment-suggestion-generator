#!/usr/bin/env python
"""
Run script for Render deployment.
Ensures correct working directory and starts the Flask server.
"""

import os
import sys
import subprocess

# Get the project root
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')

# Change to src directory and run web_server directly
os.chdir(src_path)
sys.path.insert(0, src_path)

# Run the Flask server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    
    # Import after changing directory
    from web_server import app
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
