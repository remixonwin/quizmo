"""
WSGI config for windsurf_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'windsurf_app.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    import traceback
    print(f"Error in WSGI application: {str(e)}", file=sys.stderr)
    print("Traceback:", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise
