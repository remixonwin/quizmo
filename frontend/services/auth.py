import requests
from ..utils.session import SessionManager
import streamlit as st

class AuthService:
    def __init__(self, test_mode=False):
        self.session = SessionManager()
        self.test_mode = test_mode
        
    @property
    def is_authenticated(self):
        return bool(st.session_state.get('token'))

    def login(self, username, password):
        try:
            response = requests.post(
                "http://localhost:8000/api/token/",
                json={"username": username, "password": password} 
            )
            if response.status_code == 200:
                st.session_state.token = response.json()["token"]
                return True
            return False
        except:
            return False

    def logout(self):
        if "token" in st.session_state:
            del st.session_state.token
        if "cookies" in st.session_state:
            del st.session_state.cookies

    def get_auth_headers(self):
        if not self.is_authenticated:
            return {}
        return {
            "Authorization": f"Token {st.session_state.token}"
        }

    def register(self, username, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/register/",
                json={
                    "username": username,
                    "email": email, 
                    "password": password
                }
            )
            if response.status_code == 201:
                st.session_state['token'] = response.json()['token']
                st.session_state['username'] = username
                return True
            return False
        except:
            return False