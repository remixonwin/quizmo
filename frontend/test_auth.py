import pytest
from unittest.mock import patch, MagicMock
import requests
import streamlit as st
from frontend.services.auth import AuthService

class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing"""
        return AuthService(test_mode=True)

    @pytest.fixture
    def mock_response(self):
        """Create mock response with default success values"""
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = {"token": "test-token"}
        return mock

    def test_init(self, auth_service):
        """Test AuthService initialization"""
        assert auth_service.API_URL == "http://localhost:8000/api"
        assert auth_service.test_mode == True
        assert '_session_state' in dir(auth_service)

    def test_is_authenticated_property(self, auth_service):
        """Test is_authenticated property"""
        with patch.dict('streamlit.session_state', {'token': None}):
            auth_service._session_state = st.session_state
            assert auth_service.is_authenticated == False

        with patch.dict('streamlit.session_state', {'token': 'test-token'}):
            auth_service._session_state = st.session_state
            assert auth_service.is_authenticated == True

    @patch('requests.post')
    def test_login_success(self, mock_post, auth_service, mock_response):
        """Test successful login attempt"""
        mock_post.return_value = mock_response

        result = auth_service.login("testuser", "password123")

        assert result is None
        mock_post.assert_called_with(
            f"{auth_service.API_URL}/token/",
            json={"username": "testuser", "password": "password123"}
        )
        assert auth_service._session_state['token'] == "test-token"

    @patch('requests.post')
    def test_login_invalid_credentials(self, mock_post, auth_service):
        """Test login with invalid credentials"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        result = auth_service.login("testuser", "wrongpass")

        assert result == "Invalid credentials"

    @patch('requests.post')
    def test_login_server_error(self, mock_post, auth_service):
        """Test login with server error"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        result = auth_service.login("testuser", "password123")

        assert "Login failed" in result

    @patch('requests.post')
    def test_register_success(self, mock_post, auth_service):
        """Test successful registration"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        success, message = auth_service.register(
            "newuser", "new@example.com", "password123"
        )

        assert success == True
        assert "successful" in message.lower()
        mock_post.assert_called_once()

    @patch('requests.post') 
    def test_register_duplicate_user(self, mock_post, auth_service):
        """Test registration with existing username"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "Username already exists"
        }
        mock_post.return_value = mock_response

        success, message = auth_service.register(
            "existinguser", "test@example.com", "password123"
        )

        assert success == False
        assert "exists" in message.lower()

    @patch('requests.post')
    def test_register_server_error(self, mock_post, auth_service):
        """Test registration with server error"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        success, message = auth_service.register(
            "newuser", "new@example.com", "password123"
        )

        assert success == False
        assert "failed" in message.lower()

    def test_logout(self, auth_service):
        """Test logout functionality"""
        with patch.dict('streamlit.session_state', {
            'token': 'test-token',
            'username': 'testuser'
        }):
            auth_service._session_state = st.session_state
            auth_service.logout()

            assert st.session_state['token'] is None
            assert st.session_state['username'] is None

    def test_session_state_helper(self, auth_service):
        """Test _get_session_state helper method"""
        # Test in test mode
        assert auth_service._get_session_state() == {}

        # Test in normal mode
        with patch.dict('streamlit.session_state', {}, clear=True):
            normal_auth = AuthService(test_mode=False)
            assert normal_auth._get_session_state() == st.session_state

    @patch('requests.post')
    def test_login_retry_endpoints(self, mock_post, auth_service):
        """Test login retry with multiple endpoints"""
        # First attempt fails with 404
        mock_fail = MagicMock()
        mock_fail.status_code = 404

        # Second attempt succeeds with 200
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"token": "test-token"}

        mock_post.side_effect = [mock_fail, mock_success]

        result = auth_service.login("testuser", "password123")

        assert result is None
        assert mock_post.call_count == 2
        assert auth_service._session_state['token'] == "test-token"

    @patch('requests.post')
    def test_register_invalid_email(self, mock_post, auth_service):
        """Test registration with invalid email"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "Invalid email format"
        }
        mock_post.return_value = mock_response

        success, message = auth_service.register(
            "newuser", "invalid-email", "password123"
        )

        assert success == False
        assert "invalid" in message.lower()

    def test_session_persistence(self, auth_service):
        """Test session state persistence"""
        # Mock initial state
        with patch.dict('streamlit.session_state', {'token': 'test-token', 'username': 'testuser'}):
            auth_service = AuthService(test_mode=False)
            assert 'token' in auth_service._session_state
            assert 'username' in auth_service._session_state
            assert auth_service._session_state['token'] == 'test-token'
            assert auth_service._session_state['username'] == 'testuser'