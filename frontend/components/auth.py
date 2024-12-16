import streamlit as st
from ..services.auth import AuthService
from ..components.base.form import FormComponent  # Corrected import path

class LoginForm(FormComponent):
    def __init__(self):
        super().__init__("login", "Login")
        self.auth_service = AuthService()

    def render_content(self):
        with st.container():
            st.markdown("<div data-testid='login-form'>", unsafe_allow_html=True)
            self.username = st.text_input("Username", key="login_username")
            self.password = st.text_input("Password", type="password", key="login_password")
            st.markdown("</div>", unsafe_allow_html=True)

    def handle_submit(self):
        if self.auth_service.login(self.username, self.password):
            st.session_state['token'] = 'dummy_token'
            st.session_state['username'] = self.username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")

class RegisterForm(FormComponent):
    def __init__(self):
        super().__init__("register", "Register")
        self.auth_service = AuthService()

    def render_content(self):
        with st.container():
            st.markdown("<div data-testid='register-form'>", unsafe_allow_html=True)
            self.username = st.text_input("Username", key="register_username")
            self.email = st.text_input("Email", key="register_email")
            self.password = st.text_input("Password", type="password", key="register_password")
            self.confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
            st.markdown("</div>", unsafe_allow_html=True)

    def handle_submit(self):
        if self.password != self.confirm_password:
            st.error("Passwords do not match")
            return
        
        if self.auth_service.register(self.username, self.email, self.password):
            st.session_state['username'] = self.username
            st.session_state['token'] = 'new_dummy_token'
            st.success("Registration successful!")
        else:
            st.error("Registration failed")

class PasswordResetForm(FormComponent):
    def __init__(self):
        super().__init__("reset-password", "Request Password Reset")
        self.auth = AuthService()

    def render_content(self):
        with st.container():
            st.markdown("<div data-testid='reset-password-form'>", unsafe_allow_html=True)
            self.email = st.text_input("Email", key="reset_email")
            st.markdown("</div>", unsafe_allow_html=True)

    def handle_submit(self):
        success, message = self.auth.request_password_reset(self.email)
        if success:
            st.success(message)
        else:
            st.error(message)

def login_form():
    form = LoginForm()
    form.render(form.render_content, form.handle_submit)

def register_form():
    form = RegisterForm()
    form.render(form.render_content, form.handle_submit)

def password_reset_form():
    form = PasswordResetForm()
    form.render(form.render_content, form.handle_submit)

def auth_tabs():
    auth = AuthService()
    if not auth.is_authenticated:
        tabs = st.tabs(["Login", "Register", "Reset Password"])
        with tabs[0]: login_form()
        with tabs[1]: register_form()
        with tabs[2]: password_reset_form()
    else:
        st.write("You are logged in.")
        if st.button("Logout"):
            auth.logout()
            st.rerun()

def request_password_reset(self, email):
    try:
        response = requests.post(
            f"{self.base_url}/password-reset/",
            json={"email": email}
        )
        return True, "Password reset email sent"
    except:
        return False, "Failed to send reset email"