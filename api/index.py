"""
Vercel serverless function for Django application
This file serves as the entry point for the Django app on Vercel
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hootel.settings')

# Import Django WSGI application
from hootel.wsgi import app

# This is the handler that Vercel will call
def handler(request, response):
    return app(request, response)

# For compatibility with different Vercel configurations
application = app