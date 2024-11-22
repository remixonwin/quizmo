import os
import sys
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'windsurf_app.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("WSGI application loaded successfully")
except Exception as e:
    import traceback
    print(f"Error in WSGI application: {str(e)}")
    print("Traceback:")
    print(traceback.format_exc())
