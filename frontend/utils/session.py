import os
import json
import streamlit as st

class SessionManager:
    def __init__(self):
        self.auth_dir = '.streamlit'
        self.auth_file = os.path.join(self.auth_dir, 'auth.json')
        os.makedirs(self.auth_dir, exist_ok=True)
        
        # Initialize session state
        if 'token' not in st.session_state:
            st.session_state['token'] = None
        if 'username' not in st.session_state:
            st.session_state['username'] = None

    def load_auth_state(self):
        try:
            if os.path.exists(self.auth_file):
                with open(self.auth_file, 'r') as f:
                    data = json.load(f)
                    # Update session state with loaded values
                    st.session_state['token'] = data.get('token')
                    st.session_state['username'] = data.get('username')
                    return data
        except:
            pass
        return {'token': None, 'username': None}

    def set_auth_state(self, token, username):
        try:
            st.session_state['token'] = token
            st.session_state['username'] = username
            
            with open(self.auth_file, 'w') as f:
                json.dump({'token': token, 'username': username}, f)
            return True
        except Exception as e:
            st.warning(f"Could not save session: {str(e)}")
            return False

    def clear_auth_state(self):
        st.session_state['token'] = None
        st.session_state['username'] = None
        self.set_auth_state(None, None)