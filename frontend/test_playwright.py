# frontend/test_playwright.py
import pytest
from playwright.sync_api import Page, expect  # Ensure using sync_api
from django.test import LiveServerTestCase  # Changed import to synchronous test case
from frontend.test_integration import TestMixin
import django
import json
import os
import subprocess  # Removed if not needed
import time
import threading  # Removed if not needed
from unittest.mock import patch, MagicMock
import sys
sys.setrecursionlimit(1500)  # Example: Increase recursion limit

# ...existing code...

class PlaywrightTestMixin(TestMixin):
    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        os.environ["STREAMLIT_ANALYTICS"] = "false"
        os.environ["STREAMLIT_SERVER_ADDRESS"] = "127.0.0.1"  # Changed from localhost
        os.environ["STREAMLIT_SERVER_PORT"] = "8501"
        os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "true"
        os.environ["STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION"] = "false"
        os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "200"
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
        # Add more env vars to disable analytics
        os.environ["STREAMLIT_TELEMETRY"] = "false"
        os.environ["STREAMLIT_METRICS"] = "false"
        os.environ["STREAMLIT_TRACKING"] = "false"
        os.environ["STREAMLIT_BROWSER_METRICS_ENABLED"] = "false"
        os.environ["STREAMLIT_SERVER_ANALYTICS"] = "false"
        super().setUpClass()
        
        # Start Streamlit server in a separate thread
        def run_streamlit():
            try:
                # Updated Streamlit CLI options to match current version
                cmd = [
                    "streamlit", "run",
                    "--server.address=127.0.0.1",
                    "--server.port=8501",
                    "--server.enableCORS=true",  # Corrected capitalization
                    "--server.enableWebsocketCompression=false",
                    "--server.maxUploadSize=200",
                    "--server.enableXsrfProtection=false",
                    "--browser.gatherUsageStats=false",
                    "--browser.serverPort=8501",
                    "--global.disableWidgetStateDuplicationWarning=true",  # Updated option
                    "--global.suppressDeprecationWarnings=true",
                    "frontend/main.py"
                ]
                
                DEBUG = os.getenv('STREAMLIT_TEST_DEBUG', '').lower() == 'true'

                if DEBUG:
                    print(f"Running Streamlit with command: {' '.join(cmd)}")
                
                # Use line buffering for output
                cls.streamlit_process = subprocess.Popen(
                    cmd,
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=1,  # Line buffering
                    universal_newlines=True,
                    encoding='utf-8'
                )
                
                # Monitor startup with timeout
                start_time = time.time()
                while (time.time() - start_time) < 30:  # 30 second timeout
                    if cls.streamlit_process.poll() is not None:
                        raise Exception(f"Streamlit server failed to start: {cls.streamlit_process.stderr.read()}")
                        
                    line = cls.streamlit_process.stdout.readline()
                    if "You can now view your Streamlit app in your browser." in line:
                        print("Streamlit server started successfully")
                        return
                        
                raise Exception("Streamlit server startup timed out")
            except Exception as e:
                print(f"Error starting Streamlit: {str(e)}")
                raise
                
        cls.streamlit_thread = threading.Thread(target=run_streamlit)
        cls.streamlit_thread.daemon = True
        cls.streamlit_thread.start()
        # Wait for server to start
        time.sleep(60)  # Increase initial wait time for Streamlit

    @classmethod
    def tearDownClass(cls):
        # Stop Streamlit server
        if hasattr(cls, 'streamlit_process'):
            cls.streamlit_process.terminate()
            cls.streamlit_process.wait()
        super().tearDownClass()

    @pytest.fixture(autouse=True)
    def setup_playwright(self, page: Page):
        self.page = page
        self.page.set_default_timeout(60000)
        self.page.set_viewport_size({"width": 1280, "height": 720})

    def wait_for_load(self):
        """Wait for Streamlit to be fully loaded"""
        try:
            # Wait for load states
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            
            # Wait for main Streamlit elements
            self.page.wait_for_selector("[data-testid='stAppViewContainer']", 
                                      state="attached",  # Changed from visible to attached
                                      timeout=30000)
            
            # Wait for elements to stabilize
            time.sleep(5)  # Add small delay for UI stabilization
            return True
        except Exception as e:
            print(f"Wait for load failed: {str(e)}")
            return False

    def wait_for_element(self, selector, timeout=30000):
        try:
            return self.page.wait_for_selector(selector, timeout=timeout)
        except:
            return None

    # Add debug method for form visibility issues
    def wait_for_form(self, form_key):
        """Helper to wait for Streamlit form with retry"""
        DEBUG = os.getenv('STREAMLIT_TEST_DEBUG', '').lower() == 'true'
        
        # Update selectors to match Streamlit's structure
        form_selector = f'div[data-testid="{form_key}-form"]'
        
        try:
            # Wait for form container
            self.page.wait_for_selector(form_selector, state="attached", timeout=30000)
            form = self.page.query_selector(form_selector)
            if not form:
                raise Exception(f"Form container {form_selector} not found")
                
            if DEBUG:
                print(f"\nForm container found: {form_selector}")
                
            return self.page  # Return page instead of form for consistent API
            
        except Exception as e:
            if DEBUG:
                print(f"\nForm not found: {str(e)}")
                print("\nPage content:")
                print(self.page.content())
                
            raise Exception(f"Form {form_key} failed to load: {str(e)}")

class AuthenticationTest(PlaywrightTestMixin, LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.api_url = f"{self.live_server_url}/api"
        self.login_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }

    def tearDown(self):
        super().tearDown()
        
    def wait_for_load(self):
        # Wait for Streamlit to be fully loaded
        self.page.wait_for_selector("[data-testid='stToolbar']")
        self.page.wait_for_load_state("networkidle")
        
    def test_login_form(self):
        try:
            self.page.goto("http://localhost:8501")
            self.wait_for_load()

            # Check if already logged in and logout if needed
            if self.page.get_by_text("You are logged in.").is_visible():
                self.page.get_by_role("button", name="Logout").click()
                time.sleep(1)

            # Ensure Login tab is active
            login_tab = self.page.get_by_role("tab", name="Login")
            login_tab.click()

            # Use more specific selectors scoped to login form
            self.page.get_by_label("Username", exact=True).first().fill(self.login_data['username'])
            self.page.get_by_label("Password", exact=True).first().fill(self.login_data['password'])
            
            self.page.get_by_role("button", name="Login", exact=True).click()
            # Verify successful login
            self.page.get_by_text("You are logged in.").wait_for(timeout=5000)

        except Exception as e:
            print(f"Login test failed: {str(e)}")
            print("\nPage content:")
            print(self.page.content())
            raise

    def test_registration_form(self):
        try:
            self.page.goto("http://localhost:8501")
            self.wait_for_load()
            
            # Check if already logged in and logout if needed
            if self.page.get_by_text("You are logged in.").is_visible():
                self.page.get_by_role("button", name="Logout").click()
                time.sleep(1)

            # Find Register tab by role
            register_tab = self.page.get_by_role("tab", name="Register")
            register_tab.click()
            
            # Focus within registration form using registration-form selector
            register_form = self.page.locator("[data-testid='register-form']")
            
            # Fill form using scoped selectors
            register_form.get_by_label("Username").fill(self.login_data['username'])
            register_form.get_by_label("Email").fill(self.login_data['email'])
            register_form.get_by_label("Password").fill(self.login_data['password'])
            register_form.get_by_label("Confirm Password").fill(self.login_data['password'])

            # Submit form
            register_form.get_by_role("button", name="Register").click()

            # Wait for success message
            self.page.get_by_text("Registration successful!").wait_for(timeout=5000)

        except Exception as e:
            print(f"Registration test failed: {str(e)}")
            print("\nPage content:")
            print(self.page.content())
            raise

    def test_password_reset_flow(self):
        try:
            self.page.goto("http://localhost:8501")
            self.wait_for_load()

            # Check if logged in and logout if needed  
            if self.page.get_by_text("You are logged in.").is_visible():
                self.page.get_by_role("button", name="Logout").click()
                time.sleep(1)

            # Click Reset Password tab
            reset_tab = self.page.get_by_role("tab", name="Reset Password")
            reset_tab.click()

            # Focus within reset password form
            reset_form = self.page.locator("[data-testid='reset-password-form']")
            
            # Fill form using scoped selector
            reset_form.get_by_label("Email").fill(self.login_data['email'])
            reset_form.get_by_role("button", name="Request Password Reset").click()

            # Verify success message
            self.page.get_by_text("Password reset email sent!").wait_for(timeout=5000)

        except Exception as e:
            print(f"Password reset test failed: {str(e)}")
            print("\nPage content:")
            print(self.page.content())
            raise