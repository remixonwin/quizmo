import unittest

from frontend.components.auth import LoginForm, RegisterForm, PasswordResetForm
from unittest.mock import patch

class TestAuthForms(unittest.TestCase):
    
    @patch('frontend.components.auth.AuthService')
    def test_login_form_submit_success(self, mock_auth_service):
        mock_auth_service.login.return_value = None  # Simulate successful login
        form = LoginForm()
        form.username = 'testuser'
        form.password = 'password'
        
        with patch('streamlit.session_state') as mock_session:
            form.handle_submit()
            mock_auth_service.login.assert_called_once_with('testuser', 'password')
            mock_session['token'] = 'dummy_token'
            mock_session['username'] = 'testuser'
    
    @patch('frontend.components.auth.AuthService')
    def test_register_form_submit_success(self, mock_auth_service):
        mock_auth_service.register.return_value = None  # Simulate successful registration
        form = RegisterForm()
        form.username = 'newuser'
        form.email = 'newuser@example.com'
        form.password = 'password'
        form.confirm_password = 'password'
        
        with patch('streamlit.session_state') as mock_session:
            form.handle_submit()
            mock_auth_service.register.assert_called_once_with('newuser', 'newuser@example.com', 'password')
            mock_session['token'] = 'new_dummy_token'
            mock_session['username'] = 'newuser'
    
    @patch('frontend.components.auth.AuthService')
    def test_password_reset_form_submit_success(self, mock_auth_service):
        mock_auth_service.request_password_reset.return_value = (True, "Password reset email sent")
        form = PasswordResetForm()
        form.email = 'user@example.com'
        
        with patch('streamlit.session_state') as mock_session:
            form.handle_submit()
            mock_auth_service.request_password_reset.assert_called_once_with('user@example.com')
            # Add assertions for success message if applicable

if __name__ == '__main__':
    unittest.main()
