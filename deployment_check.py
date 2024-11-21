import sys
import os
import pkg_resources
import platform
import socket
import django
from django.conf import settings
import psycopg2
import redis

def check_python_version():
    print("\n=== Python Version Check ===")
    print(f"Python Version: {platform.python_version()}")
    if sys.version_info >= (3, 11):
        print("✓ Python version is 3.11 or higher")
    else:
        print("⚠ Python version is below 3.11")

def check_dependencies():
    print("\n=== Dependencies Check ===")
    required = pkg_resources.parse_requirements(open('requirements.txt'))
    for req in required:
        try:
            pkg_resources.require(str(req))
            print(f"✓ {req.name} is installed")
        except pkg_resources.DistributionNotFound:
            print(f"⚠ Missing: {req.name}")
        except pkg_resources.VersionConflict:
            print(f"⚠ Version conflict: {req.name}")

def check_django_settings():
    print("\n=== Django Settings Check ===")
    try:
        print(f"Django Version: {django.get_version()}")
        print(f"Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not Set')}")
        print(f"Debug Mode: {settings.DEBUG}")
        print(f"Allowed Hosts: {settings.ALLOWED_HOSTS}")
        print(f"Database Engine: {settings.DATABASES['default']['ENGINE']}")
        print("✓ Django settings loaded successfully")
    except Exception as e:
        print(f"⚠ Django settings error: {str(e)}")

def check_database():
    print("\n=== Database Connection Check ===")
    try:
        db_settings = settings.DATABASES['default']
        conn = psycopg2.connect(
            dbname=db_settings['NAME'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            host=db_settings['HOST'],
            port=db_settings['PORT']
        )
        print("✓ Successfully connected to PostgreSQL")
        conn.close()
    except Exception as e:
        print(f"⚠ Database connection error: {str(e)}")

def check_redis():
    print("\n=== Redis Connection Check ===")
    try:
        redis_client = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
        redis_client.ping()
        print("✓ Successfully connected to Redis")
    except Exception as e:
        print(f"⚠ Redis connection error: {str(e)}")

def check_static_files():
    print("\n=== Static Files Check ===")
    print(f"Static Root: {settings.STATIC_ROOT}")
    print(f"Static URL: {settings.STATIC_URL}")
    if os.path.exists(settings.STATIC_ROOT):
        print("✓ Static root directory exists")
    else:
        print("⚠ Static root directory does not exist")

def check_media_files():
    print("\n=== Media Files Check ===")
    print(f"Media Root: {settings.MEDIA_ROOT}")
    print(f"Media URL: {settings.MEDIA_URL}")
    if os.path.exists(settings.MEDIA_ROOT):
        print("✓ Media root directory exists")
    else:
        print("⚠ Media root directory does not exist")

def check_security_settings():
    print("\n=== Security Settings Check ===")
    security_settings = [
        ('SECURE_SSL_REDIRECT', getattr(settings, 'SECURE_SSL_REDIRECT', False)),
        ('SESSION_COOKIE_SECURE', getattr(settings, 'SESSION_COOKIE_SECURE', False)),
        ('CSRF_COOKIE_SECURE', getattr(settings, 'CSRF_COOKIE_SECURE', False)),
        ('SECURE_BROWSER_XSS_FILTER', getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False)),
        ('SECURE_CONTENT_TYPE_NOSNIFF', getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False))
    ]
    for setting, value in security_settings:
        status = "✓" if value else "⚠"
        print(f"{status} {setting}: {value}")

def main():
    print("=== Starting Deployment Check ===")
    check_python_version()
    check_dependencies()
    check_django_settings()
    check_database()
    check_redis()
    check_static_files()
    check_media_files()
    check_security_settings()
    print("\n=== Deployment Check Complete ===")

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'windsurf_app.settings_digitalocean')
    django.setup()
    main()
