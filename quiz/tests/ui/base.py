"""
Base class for UI tests.
"""
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class BaseUITest(StaticLiveServerTestCase):
    """Base class for UI tests using Selenium."""

    def setUp(self):
        """Set up test browser."""
        # Set up Firefox in headless mode
        options = Options()
        options.add_argument('--headless')
        service = Service(executable_path='/snap/bin/geckodriver')
        self.browser = webdriver.Firefox(options=options, service=service)
        self.browser.implicitly_wait(10)

    def tearDown(self):
        """Clean up test browser."""
        if hasattr(self, 'browser'):
            self.browser.quit()

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and visible."""
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None

    def login(self, username, password):
        """Log in a user."""
        # Navigate to login page using reverse URL
        login_url = reverse('quiz:login')
        full_url = f"{self.live_server_url}{login_url}"
        logger.info(f"Navigating to login URL: {full_url}")
        self.browser.get(full_url)

        # Log page source for debugging
        logger.info("Page source:")
        logger.info(self.browser.page_source)

        # Fill in login form - using crispy-forms IDs
        username_input = self.wait_for_element(By.ID, "id_username")  # Try ID first
        if not username_input:
            logger.info("Could not find username by ID, trying name attribute")
            username_input = self.wait_for_element(By.NAME, "username")

        password_input = self.wait_for_element(By.ID, "id_password")  # Try ID first
        if not password_input:
            logger.info("Could not find password by ID, trying name attribute")
            password_input = self.wait_for_element(By.NAME, "password")

        submit_button = self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")

        if not all([username_input, password_input, submit_button]):
            logger.error("Missing form elements:")
            logger.error(f"Username input found: {username_input is not None}")
            logger.error(f"Password input found: {password_input is not None}")
            logger.error(f"Submit button found: {submit_button is not None}")
            self.fail("Could not find login form elements")

        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button.click()

        # Wait for redirect to dashboard
        self.wait_for_element(By.CLASS_NAME, "dashboard")
