import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TestAuthentication:
    def test_login_page_loads(self, browser, live_server_url):
        """Test that the login page loads successfully."""
        browser.get(f"{live_server_url}/login/")
        # Wait for the page title to be present
        try:
            WebDriverWait(browser, 10).until(
                lambda driver: "Login" in driver.title
            )
        except TimeoutException:
            pytest.fail("Login page did not load properly")
        
    def test_login_form_elements(self, browser, live_server_url):
        """Test that all login form elements are present."""
        browser.get(f"{live_server_url}/login/")
        
        try:
            # Wait for form elements to be present
            username_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            login_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
            )
            
            # Check if elements are visible
            assert username_field.is_displayed(), "Username field is not visible"
            assert password_field.is_displayed(), "Password field is not visible"
            assert login_button.is_displayed(), "Login button is not visible"
            
        except TimeoutException:
            pytest.fail("Login form elements did not load properly")
        
    def test_failed_login(self, browser, live_server_url):
        """Test login failure with invalid credentials."""
        browser.get(f"{live_server_url}/login/")
        
        try:
            # Wait for and fill in form elements
            username_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            login_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
            )
            
            username_field.send_keys("invalid_user")
            password_field.send_keys("invalid_password")
            login_button.click()
            
            # Wait for error message
            error_message = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
            )
            assert error_message.is_displayed(), "Error message is not visible"
            
        except TimeoutException:
            pytest.fail("Failed login test did not complete properly")
