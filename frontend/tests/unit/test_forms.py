import unittest
from frontend.components.auth import LoginForm, RegisterForm
from frontend.components.quiz import create_question_form
from unittest.mock import patch

class TestForms(unittest.TestCase):
    
    @patch('frontend.components.auth.AuthService')
    def test_login_form_validation(self, mock_auth_service):
        form = LoginForm()
        form.username = 'user'
        form.password = 'pass'
        
        with patch('streamlit.session_state') as mock_session:
            form.handle_submit()
            mock_auth_service.login.assert_called_with('user', 'pass')
            mock_session.__setitem__.assert_any_call('token', 'dummy_token')
            mock_session.__setitem__.assert_any_call('username', 'user')
    
    @patch('frontend.components.auth.AuthService')
    def test_register_form_password_mismatch(self, mock_auth_service):
        form = RegisterForm()
        form.username = 'newuser'
        form.email = 'new@example.com'
        form.password = 'pass1'
        form.confirm_password = 'pass2'
        
        with patch('streamlit.session_state') as mock_session:
            form.handle_submit()
            mock_auth_service.register.assert_not_called()
            mock_session.__setitem__.assert_not_called()
    
    def test_create_question_form_empty(self):
        with patch('frontend.components.quiz.st') as mock_st:
            mock_st.text_area.return_value = ''
            question = create_question_form(0)
            self.assertIsNone(question)

if __name__ == '__main__':
    unittest.main()
