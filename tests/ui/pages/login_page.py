"""
Page Object Model for the login page.
This follows the Page Object Pattern to encapsulate the structure and behavior of the UI.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    def __init__(self, browser):
        self.browser = browser
        self.wait = WebDriverWait(browser, 10)
    
    def navigate(self, url):
        """Navigate to the login page."""
        self.browser.get(f"{url}/login/")
    
    def get_username_field(self):
        """Get the username input field."""
        return self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
    
    def get_password_field(self):
        """Get the password input field."""
        return self.browser.find_element(By.NAME, "password")
    
    def get_login_button(self):
        """Get the login submit button."""
        return self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    
    def login(self, username, password):
        """Perform login with given credentials."""
        self.get_username_field().send_keys(username)
        self.get_password_field().send_keys(password)
        self.get_login_button().click()
    
    def get_error_message(self):
        """Get the error message element after failed login."""
        return self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
