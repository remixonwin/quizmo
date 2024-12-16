import unittest
from frontend.utils.session import SessionManager
from unittest.mock import patch

class TestSessionManager(unittest.TestCase):
    
    def setUp(self):
        self.session_manager = SessionManager()
    
    def test_initial_state(self):
        with patch('streamlit.session_state', {}) as mock_session_state:
            self.session_manager.load_auth_state()
            self.assertIsNone(mock_session_state.get('token'))
    
    def test_set_auth_state(self):
        with patch('streamlit.session_state', {}) as mock_session_state:
            self.session_manager.set_auth_state('test_token', 'test_user')
            self.assertEqual(mock_session_state['token'], 'test_token')
            self.assertEqual(mock_session_state['username'], 'test_user')
    
    def test_clear_auth_state(self):
        with patch('streamlit.session_state', {}) as mock_session_state:
            self.session_manager.clear_auth_state()
            self.assertIsNone(mock_session_state.get('token'))
            self.assertIsNone(mock_session_state.get('username'))

if __name__ == '__main__':
    unittest.main()
