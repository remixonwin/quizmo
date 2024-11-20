"""
WSGI config for windsurf_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'windsurf_app.settings')

try:
    # Get the WSGI application
    application = get_wsgi_application()
    
    # Wrap the application with WhiteNoise
    application = WhiteNoise(application)
    application.add_files(os.path.join(BASE_DIR, 'staticfiles'), prefix='static/')
    
except Exception as e:
    print(f"Error initializing WSGI application: {e}", file=sys.stderr)
    raise
