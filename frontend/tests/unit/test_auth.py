import unittest

from frontend.components.auth import LoginForm, RegisterForm, PasswordResetForm
from unittest.mock import patch, Mock

class TestAuthForms(unittest.TestCase):
    
    @patch('frontend.components.auth.AuthService')
    def test_login_form_submit_success(self, mock_auth_service):
        mock_auth = Mock()
        mock_auth.login.return_value = True
        mock_auth_service.return_value = mock_auth
        
        form = LoginForm()
        form.username = 'testuser'
        form.password = 'password'
        
        with patch('streamlit.session_state', {}) as mock_session:
            form.handle_submit()
            mock_auth.login.assert_called_once_with('testuser', 'password')
    
    @patch('frontend.components.auth.AuthService')
    def test_register_form_submit_success(self, mock_auth_service):
        mock_instance = mock_auth_service.return_value
        mock_instance.register.return_value = True
        
        form = RegisterForm()
        form.username = 'testuser'
        form.email = 'test@example.com'
        form.password = 'password123'
        form.confirm_password = 'password123'
        
        with patch('streamlit.session_state', {}) as mock_session:
            form.handle_submit()
            mock_instance.register.assert_called_once_with(
                'testuser', 
                'test@example.com',
                'password123'
            )
    
    @patch('frontend.components.auth.AuthService')
    def test_password_reset_form_submit_success(self, mock_auth_service):
        mock_instance = mock_auth_service.return_value
        mock_instance.request_password_reset.return_value = (True, "Password reset email sent")
        form = PasswordResetForm()
        form.email = 'user@example.com'
        
        with patch('streamlit.session_state', {}) as mock_session:
            form.handle_submit()
            mock_instance.request_password_reset.assert_called_once_with('user@example.com')

if __name__ == '__main__':
    unittest.main()
