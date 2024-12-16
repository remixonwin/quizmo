import streamlit as st
from frontend.components.auth import auth_tabs
from frontend.components.quiz import quiz_list, quiz_create_form 
from frontend.services.auth import AuthService
import subprocess
import os

def check_backend():
    """Check if Django backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=2)
        return response.status_code == 200
    except:
        return False

def init_session_state():
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'should_rerun' not in st.session_state:
        st.session_state.should_rerun = False

def main():
    st.set_page_config(page_title="Quiz App", page_icon="📚")
    init_session_state()
    
    st.title("🌐 Quiz App")

    # Check backend status
    if not check_backend():
        st.error("⚠️ Backend server is not running. Please start it with:")
        st.code("python manage.py runserver", language="bash")
        return

    auth_service = AuthService()
    auth_tabs()
    
    if auth_service.is_authenticated:
        col1, col2 = st.columns([2, 1])
        with col1:
            quiz_list()
        with col2:
            st.header("Quick Actions")
            if st.button("Create New Quiz"):
                st.session_state["show_create_form"] = True

        if st.session_state.get("show_create_form", False):
            quiz_create_form()
    else:
        st.info("Please login or register to access quizzes")

if __name__ == "__main__":
    main()