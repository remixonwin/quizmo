import sys
import os
import platform
import django
from django.core.management import execute_from_command_line

def check_environment():
    print("\n=== Environment Check ===")
    print(f"Python Version: {platform.python_version()}")
    print(f"Django Version: {django.get_version()}")
    print(f"Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not Set')}")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Python Path: {sys.executable}")

def check_django_config():
    print("\n=== Django Configuration Check ===")
    try:
        execute_from_command_line(['manage.py', 'check', '--deploy'])
    except Exception as e:
        print(f"Error during Django check: {str(e)}")

def main():
    print("=== Starting Quick Deployment Check ===")
    check_environment()
    check_django_config()
    print("\n=== Quick Deployment Check Complete ===")

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'windsurf_app.settings_digitalocean')
    django.setup()
    main()
