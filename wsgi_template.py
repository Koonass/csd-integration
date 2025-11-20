"""
WSGI configuration for PythonAnywhere deployment

INSTRUCTIONS:
1. In PythonAnywhere Web tab, click your WSGI configuration file
2. DELETE ALL existing content
3. COPY this entire file
4. PASTE into the WSGI configuration file
5. REPLACE 'yourusername' with your actual PythonAnywhere username (4 places)
6. SAVE the file
7. Reload your web app
"""

import sys
import os

# Add your project directory to the sys.path
# REPLACE 'yourusername' with your actual username!
project_home = '/home/yourusername/csd-integration'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Activate virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Flask app
from app import app as application

# This allows PythonAnywhere to serve your Flask app
