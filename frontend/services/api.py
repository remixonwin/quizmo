import os
import requests
import streamlit as st
from requests.exceptions import ConnectionError, Timeout

class APIClient:
    def __init__(self):
        self.base_url = os.getenv('API_URL', "http://localhost:8000/api")
        
    def get(self, endpoint, headers=None):
        try:
            return requests.get(f"{self.base_url}/{endpoint.lstrip('/')}", headers=headers)
        except (ConnectionError, Timeout) as e:
            st.error("⚠️ Cannot connect to server. Please ensure the backend is running.")
            return None
        
    def post(self, endpoint, data=None, headers=None):
        try:
            return requests.post(f"{self.base_url}/{endpoint.lstrip('/')}", 
                               json=data, 
                               headers=headers)
        except (ConnectionError, Timeout) as e:
            st.error("⚠️ Cannot connect to server. Please ensure the backend is running.")
            return None

    def delete(self, endpoint, headers=None):
        try:
            return requests.delete(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=headers
            )
        except (ConnectionError, Timeout) as e:
            st.error("⚠️ Cannot connect to server. Please ensure the backend is running.")
            return None