import requests
from ..utils.session import SessionManager
import streamlit as st

class AuthService:
    def __init__(self, test_mode=False):
        self.API_URL = "http://localhost:8000/api"
        self.test_mode = test_mode
        self._session_state = self._get_session_state()
        self.max_retries = 2  # Added retry limit

    @property
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated based on the session token."""
        return bool(self._session_state.get('token'))

    def login(self, username: str, password: str):
        """Attempt to log in the user with retry."""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.API_URL}/token/",
                    json={"username": username, "password": password}
                )
                if response.status_code == 200:
                    self._session_state['token'] = response.json().get('token')
                    self._session_state['username'] = username
                    return None
                elif response.status_code == 401:
                    return "Invalid credentials"
                else:
                    continue  # Retry on unexpected status codes
            except requests.exceptions.ConnectionError:
                continue  # Retry on connection errors
        return "Login failed"

    def logout(self):
        """Log out the user by clearing the session state."""
        self._session_state['token'] = None
        self._session_state['username'] = None

    def register(self, username: str, email: str, password: str):
        """Register a new user."""
        try:
            response = requests.post(
                f"{self.API_URL}/register/",
                json={"username": username, "email": email, "password": password}
            )
            if response.status_code == 201:
                return True, "Registration successful"
            else:
                error_msg = response.json().get('error', 'Registration failed')
                return False, error_msg
        except requests.exceptions.ConnectionError:
            return False, "Registration failed"

    def _get_session_state(self):
        """Helper method to get the session state."""
        if self.test_mode:
            return {}
        return st.session_state