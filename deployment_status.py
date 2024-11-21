import sys
import os
import platform
import subprocess
import socket
from importlib import util
from pathlib import Path

class DeploymentCheck:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []

    def add_issue(self, message):
        self.issues.append(f"❌ {message}")

    def add_warning(self, message):
        self.warnings.append(f"⚠️ {message}")

    def add_success(self, message):
        self.successes.append(f"✅ {message}")

    def check_python_version(self):
        print("\n=== Python Version Check ===")
        version = platform.python_version()
        print(f"Current Python version: {version}")
        
        major, minor, _ = map(int, version.split('.'))
        if (major == 3 and minor == 11):
            self.add_success("Python version 3.11.x detected")
        else:
            self.add_issue(f"Python version mismatch. Found {version}, need 3.11.x")

    def check_package(self, package_name):
        spec = util.find_spec(package_name)
        if spec is not None:
            try:
                module = __import__(package_name)
                version = getattr(module, '__version__', 'unknown version')
                self.add_success(f"{package_name} ({version}) is installed")
            except ImportError:
                self.add_warning(f"{package_name} found but failed to import")
        else:
            self.add_issue(f"{package_name} is not installed")

    def check_dependencies(self):
        print("\n=== Dependencies Check ===")
        critical_packages = [
            'django',
            'psycopg2',
            'redis',
            'gunicorn',
            'whitenoise',
        ]
        
        for package in critical_packages:
            self.check_package(package)

    def check_django_settings(self):
        print("\n=== Django Settings Check ===")
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
        if settings_module:
            self.add_success(f"DJANGO_SETTINGS_MODULE is set to {settings_module}")
        else:
            self.add_issue("DJANGO_SETTINGS_MODULE is not set")

    def check_database(self):
        print("\n=== Database Configuration Check ===")
        try:
            import psycopg2
            # Note: Using the known password from the previous session
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="Bulls-eye87543",
                host="localhost",
                port="5432"
            )
            conn.close()
            self.add_success("Successfully connected to PostgreSQL database")
        except ImportError:
            self.add_issue("PostgreSQL driver (psycopg2) is not installed")
        except Exception as e:
            self.add_issue(f"Database connection failed: {str(e)}")

    def check_redis(self):
        print("\n=== Redis Check ===")
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            self.add_success("Successfully connected to Redis")
        except ImportError:
            self.add_issue("Redis package is not installed")
        except Exception as e:
            self.add_issue(f"Redis connection failed: {str(e)}")

    def check_static_files(self):
        print("\n=== Static Files Check ===")
        static_root = os.path.join(os.getcwd(), 'static')
        if os.path.exists(static_root):
            self.add_success("Static root directory exists")
        else:
            self.add_warning("Static root directory not found")

    def check_gunicorn(self):
        print("\n=== Gunicorn Check ===")
        try:
            result = subprocess.run(['gunicorn', '--version'], 
                                 capture_output=True, 
                                 text=True)
            if result.returncode == 0:
                self.add_success(f"Gunicorn is installed: {result.stdout.strip()}")
            else:
                self.add_issue("Gunicorn check failed")
        except FileNotFoundError:
            self.add_issue("Gunicorn is not installed or not in PATH")

    def run_all_checks(self):
        print("=== Starting Deployment Status Check ===")
        self.check_python_version()
        self.check_dependencies()
        self.check_django_settings()
        self.check_database()
        self.check_redis()
        self.check_static_files()
        self.check_gunicorn()

        print("\n=== Check Results ===")
        if self.successes:
            print("\nSuccesses:")
            for success in self.successes:
                print(success)
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(warning)
        
        if self.issues:
            print("\nIssues:")
            for issue in self.issues:
                print(issue)

        print("\n=== Summary ===")
        print(f"Total Successes: {len(self.successes)}")
        print(f"Total Warnings: {len(self.warnings)}")
        print(f"Total Issues: {len(self.issues)}")

if __name__ == "__main__":
    checker = DeploymentCheck()
    checker.run_all_checks()
