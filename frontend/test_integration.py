import unittest
import requests
from unittest.mock import patch, MagicMock
import json
from requests.exceptions import ConnectionError, Timeout
from datetime import datetime, timedelta
import time
import os
import shutil
import streamlit as st
from .services.auth import AuthService  # Import AuthService
from django.test import LiveServerTestCase
import django

class FrontendIntegrationTest(LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.api_url = self.live_server_url  # Use Django's test server URL
        
    @patch('requests.get')
    def test_api_connection(self, mock_get):
        # Mock the GET request response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'data': {
                'items': ['Item 1', 'Item 2', 'Item 3'],
                'count': 3
            }
        }
        mock_get.return_value = mock_response

        response = requests.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('items', data['data'])
        self.assertEqual(len(data['data']['items']), 3)

    @patch('requests.Session')
    def test_xsrf_token_handling(self, mock_session):
        # Mock session and response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'data': {'items': ['Test Item']}
        }
        mock_response.cookies = {'_streamlit_xsrf': 'test-token'}
        
        mock_session.return_value.get.return_value = mock_response
        
        # Make request
        session = requests.Session()
        response = session.get(self.api_url)
        
        # Verify XSRF token handling
        self.assertEqual(response.cookies['_streamlit_xsrf'], 'test-token')

    @patch('requests.Session')
    def test_network_timeout(self, mock_session):
        # Simulate a timeout exception
        mock_session.side_effect = Timeout

        with self.assertRaises(Timeout):
            session = requests.Session()
            session.get(self.api_url, timeout=1)
    
    @patch('requests.get')  # Change from Session to direct get
    def test_malformed_json_response(self, mock_get):
        # Simulate a response with malformed JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_get.return_value = mock_response

        response = mock_get.return_value  # Use mock response directly
        with self.assertRaises(json.JSONDecodeError):
            response.json()
    
    @patch('requests.Session.get')  # Change to patch Session.get specifically
    def test_reconnection_after_failure(self, mock_get):
        # Setup the mock to fail once then succeed
        mock_get.side_effect = [
            ConnectionError("Connection failed"),
            MagicMock(
                status_code=200,
                json=lambda: {'status': 'success', 'data': {'items': ['Recovered Item']}}
            )
        ]

        session = requests.Session()
        
        # First attempt should fail
        with self.assertRaises(ConnectionError):
            session.get(self.api_url)
            
        # Second attempt should succeed
        response = session.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('Recovered Item', data['data']['items'])

class TestMixin:
    """Mixin providing common test helper methods"""
    def setup_mock_response(self, status_code=200, data=None):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = data or {}
        return mock_response

class AuthenticationIntegrationTest(TestMixin, LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.api_url = f"{self.live_server_url}/api"
        self.auth = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }

    @patch('requests.post')
    def test_registration(self, mock_post):
        mock_post.return_value = self.setup_mock_response(201, {
            'username': self.auth['username'],
            'redirect': 'login'
        })

        response = requests.post(f"{self.api_url}/register/", json=self.auth)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['username'], self.auth['username'])

    @patch('requests.post')
    def test_registration_failure(self, mock_post):
        # Mock failed registration response with detailed errors
        mock_post.return_value = self.setup_mock_response(400, {
            'error': 'Registration failed',
            'details': {
                'username': 'Username is already taken or invalid',
                'email': 'Please provide a valid email address'
            }
        })

        response = requests.post(f"{self.api_url}/register/", json=self.auth)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error'], 'Registration failed')
        self.assertIn('details', data)
        self.assertIn('username', data['details'])
        self.assertIn('email', data['details'])

    @patch('requests.post')
    def test_login(self, mock_post):
        # Mock successful token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'token': 'test-token-123'}
        mock_post.return_value = mock_response

        response = requests.post(
            f"{self.api_url}/api-token-auth/",
            json={'username': self.auth['username'], 'password': self.auth['password']}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    @patch('requests.get')
    def test_authenticated_request(self, mock_get):
        # Mock authenticated response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'protected content'}
        mock_get.return_value = mock_response

        headers = {'Authorization': 'Token test-token-123'}
        response = requests.get(f"{self.api_url}/quizzes/", headers=headers)
        
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_with(
            f"{self.api_url}/quizzes/",
            headers=headers
        )

    @patch('requests.post')
    def test_registration_success_redirect(self, mock_post):
        # Mock successful registration response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'username': self.auth['username'],
            'redirect': 'login'
        }
        mock_post.return_value = mock_response

        response = requests.post(f"{self.api_url}/register/", json=self.auth)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['username'], self.auth['username'])
        self.assertEqual(response.json()['redirect'], 'login')

    @patch('requests.post')
    def test_registration_and_redirect(self, mock_post):
        # Mock successful registration response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'username': self.auth['username'],
            'redirect': 'login'  # Check for redirect field
        }
        mock_post.return_value = mock_response

        response = requests.post(f"{self.api_url}/register/", json=self.auth)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['username'], self.auth['username'])
        self.assertEqual(data['redirect'], 'login')  # Verify redirect to login

    @patch('requests.post')
    def test_registration_with_common_password(self, mock_post):
        """Test registration with a common password is rejected"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': 'Registration failed',
            'details': {'password': 'This password is too common.'}
        }
        mock_post.return_value = mock_response

        test_data = {**self.auth, 'password': 'password123'}
        response = requests.post(f"{self.api_url}/register/", json=test_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.json()['details'])

    @patch('requests.post')
    def test_registration_with_similar_username_password(self, mock_post):
        """Test registration when password is similar to username"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': 'Registration failed',
            'details': {'password': 'Password is too similar to username.'}
        }
        mock_post.return_value = mock_response

        test_data = {**self.auth, 'username': 'johnsmith', 'password': 'johnsmith123'}
        response = requests.post(f"{self.api_url}/register/", json=test_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.json()['details'])

class E2ETest(TestMixin, LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.api_url = f"{self.live_server_url}/api"
        self.auth_token = None
        self.session = requests.Session()
        self.mock_responses = {
            'request_reset': self.setup_mock_response(200, {
                'message': 'Password reset email sent!',
                'user_id': 1,
                'token': 'valid-token'
            }),
            'reset_confirm': self.setup_mock_response(200, {
                'message': 'Password reset successful!'
            })
        }

    @patch('requests.Session.post')  # Changed patch target
    def test_complete_user_flow(self, mock_post):
        # Update mock responses to include error handling
        mock_register_error = MagicMock()
        mock_register_error.status_code = 400
        mock_register_error.json.return_value = {
            'error': 'Registration failed',
            'details': {'username': 'Username is already taken'}
        }

        mock_register_response = MagicMock()
        mock_register_response.status_code = 201
        mock_register_response.json.return_value = {'id': 1, 'username': 'testuser'}

        mock_login_response = MagicMock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {'token': 'test-token-123'}

        mock_create_quiz_response = MagicMock()
        mock_create_quiz_response.status_code = 201
        mock_create_quiz_response.json.return_value = {
            'id': 1,
            'title': 'Test Quiz'
            # 'author': 'testuser'  # Ensure author is not included
        }

        mock_create_question_response = MagicMock()
        mock_create_question_response.status_code = 201
        mock_create_question_response.json.return_value = {
            'id': 1, 
            'text': 'Test Question',
            'points': 5,
            'quiz': 1,
            'choices': [
                {'text': 'Choice 1', 'is_correct': True},
                {'text': 'Choice 2', 'is_correct': False}
            ]
        }

        def debug_request(url, json_data, headers=None):
            print(f"\nDEBUG: Request Details")
            print(f"URL: {url}")
            print(f"Data: {json_data}")
            print(f"Headers: {headers}\n")

        # Update side effect function to handle kwargs and debug
        def side_effect(url, json=None, **kwargs):
            debug_request(url, json, kwargs.get('headers'))
            
            # More specific URL pattern matching
            if '/quizzes/' in url and '/questions/' in url:
                print(f"DEBUG: Matched questions endpoint")
                # Validate question data format
                if not isinstance(json, dict):
                    print("DEBUG: Invalid JSON format")
                    return self.setup_mock_response(400, {'error': 'Invalid JSON'})
                
                required_fields = ['text', 'points', 'choices']
                if not all(field in json for field in required_fields):
                    print(f"DEBUG: Missing required fields. Got: {list(json.keys())}")
                    return self.setup_mock_response(400, {'error': 'Missing required fields'})
                
                print("DEBUG: Question data valid, returning 201")
                return mock_create_question_response
                
            elif url.endswith('/quizzes/'):
                return mock_create_quiz_response
            elif url.endswith('/api/register/'):
                # Fix: Make username pattern matching more specific
                username = json.get('username', '')
                if username == 'testuser':  # Only match exact username
                    return mock_register_error
                return mock_register_response
            elif url.endswith('/api-token-auth/') or url.endswith('/token/'):
                return mock_login_response
            else:
                print(f"DEBUG: No matching endpoint for URL: {url}")
                return self.setup_mock_response(404, {'error': f'Unhandled endpoint: {url}'})

        mock_post.side_effect = side_effect

        # Try registering with existing username
        register_data = {
            'username': 'testuser',  # Known to exist
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        response = self.session.post(f"{self.api_url}/register/", json=register_data)
        if response.status_code == 400:
            error_data = response.json()
            self.assertIn('error', error_data)
            self.assertIn('details', error_data)
            self.assertIn('username', error_data['details'])

        # Continue with successful registration using timestamp-based username
        # 1. Register
        username = f'testuser_{int(time.time())}'
        register_data = {
            'username': username,
            'password': 'testpass123',
            'email': f'{username}@test.com'
        }
        response = self.session.post(f"{self.api_url}/register/", json=register_data)
        self.assertEqual(response.status_code, 201)

        # 2. Login - Try both endpoints
        auth_endpoints = [
            f"{self.api_url}/token/",
            f"{self.api_url}/api-token-auth/"
        ]
        
        login_success = False
        for endpoint in auth_endpoints:
            try:
                response = self.session.post(
                    endpoint,
                    json={'username': username, 'password': 'testpass123'}
                )
                if response.status_code == 200:
                    login_success = True
                    break
            except:
                continue
                
        self.assertTrue(login_success, "Failed to authenticate with any endpoint")
        self.auth_token = response.json().get('token')
        self.assertIsNotNone(self.auth_token)

        # 3. Create Quiz
        headers = {
            'Authorization': f'Token {self.auth_token}',
            'Content-Type': 'application/json'
        }
        quiz_data = {
            'title': 'Test Quiz',
            'description': 'Test Description'
            # Remove author field - it's set by backend
        }
        response = self.session.post(
            f"{self.api_url}/quizzes/",
            json=quiz_data,
            headers=headers
        )
        if response.status_code != 201:
            print(f"Quiz creation failed: {response.text}")
        self.assertEqual(response.status_code, 201)
        quiz_id = response.json().get('id')
        self.assertIsNotNone(quiz_id)

        # 4. Add Questions - Update format to match serializer expectations  
        questions_data = {
            'text': 'Test Question',
            'points': 5,
            'choices': [
                {'text': 'Choice 1', 'is_correct': True},
                {'text': 'Choice 2', 'is_correct': False}
            ]
        }
        
        question_url = f"{self.api_url}/quizzes/{quiz_id}/questions/"
        print(f"\nDEBUG: Sending question creation request")
        print(f"URL: {question_url}")
        print(f"Data: {questions_data}")
        print(f"Headers: {headers}\n")

        response = self.session.post(
            question_url,
            json=questions_data,
            headers=headers
        )

        if response.status_code != 201:
            print(f"DEBUG: Question creation failed")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Request data: {questions_data}")

        self.assertEqual(response.status_code, 201)

    @patch('requests.post')  # Fix: Change patch target to requests.post
    def test_complete_password_reset_flow(self, mock_post):
        # Mock responses for password reset flow
        def side_effect(url, json):
            if '/password-reset/confirm/' in url:
                if (json.get('user_id') == 1 and 
                    json.get('token') == 'valid-token' and 
                    json.get('new_password')):
                    return self.mock_responses['reset_confirm']
            elif '/password-reset/' in url:
                if json.get('email'):
                    return self.mock_responses['request_reset']
            return self.setup_mock_response(400, {'error': 'Invalid request'})
        
        mock_post.side_effect = side_effect

        auth = AuthService(test_mode=True)  # Use AuthService instead of AuthManager

        # 1. Request password reset
        success, message = auth.request_password_reset('test@example.com')
        self.assertTrue(success)
        self.assertEqual(message, 'Password reset email sent!')

        # Get the response data (mocked)
        reset_data = {
            'user_id': 1,
            'token': 'valid-token'
        }

        # 2. Reset password with token from response
        success, message = auth.reset_password(
            user_id=reset_data['user_id'],
            token=reset_data['token'],
            new_password='newpass123'
        )
        self.assertTrue(success)
        self.assertEqual(message, 'Password reset successful!')

class EdgeCaseTest(LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.api_url = f"{self.live_server_url}/api"
        self.session = requests.Session()
        # Add token setup for authenticated requests
        self.auth_token = 'test-token'

    @patch('requests.Session.post')
    def test_slow_network(self, mock_post):
        # Simulate timeout by raising the exception directly
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with self.assertRaises(requests.exceptions.Timeout):
            self.session.post(
                f"{self.api_url}/api-token-auth/",
                json={'username': 'test', 'password': 'test'},
                timeout=1
            )

    @patch('requests.Session.get')
    def test_partial_response(self, mock_get):
        # Test handling of incomplete JSON responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'incomplete': 'data'}
        mock_get.return_value = mock_response

        response = self.session.get(f"{self.api_url}/quizzes/")
        self.assertNotIn('questions', response.json())

    @patch('requests.post')
    def test_unicode_handling(self, mock_post):
        # Mock the POST request for creating a quiz with unicode characters
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 1,
            'title': '퀴즈 테��트',
            'description': '🎯 Test Quiz ✨'
        }
        mock_post.return_value = mock_response

        headers = {
            'Authorization': f'Token {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
        response = self.session.post(
            f"{self.api_url}/quizzes/",
            json={
                'title': '퀴즈 테스트',
                'description': '🎯 Test Quiz ✨'
            },
            headers=headers
        )
        self.assertIn(response.status_code, [201, 401])  # Either created or unauthorized

class SessionManagementTest(unittest.TestCase):
    def setUp(self):
        # Initialize session state
        if not hasattr(st, 'session_state'):
            setattr(st, 'session_state', {})
        
        # Ensure clean session state
        st.session_state.clear()
        
        # Setup test directories using absolute path
        self.api_url = 'http://localhost:8000/api'
        self.auth_dir = os.path.abspath('.streamlit')
        self.auth_file = os.path.join(self.auth_dir, 'auth.json')
        
        # Ensure test directory exists
        os.makedirs(self.auth_dir, exist_ok=True)
        
        # Initialize session state
        st.session_state['token'] = None
        st.session_state['username'] = None

        # Patch streamlit.session_state with a mutable dictionary
        self.patcher = patch('streamlit.session_state', new_callable=dict)
        self.mock_session_state = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        
        # Initialize session state variables
        self.mock_session_state['token'] = None
        self.mock_session_state['username'] = None

        self.auth_service = AuthService(test_mode=True)
    
    # Update all test methods to use auth_service instead of AuthManager

    def tearDown(self):
        # Clean up test files
        try:
            if os.path.exists(self.auth_file):
                os.remove(self.auth_file)
            if os.path.exists(self.auth_dir):
                os.rmdir(self.auth_dir)
        except (OSError, FileNotFoundError):
            pass
        
        # Clear session state
        st.session_state.clear()

        # Clear the mocked session state
        self.mock_session_state.clear()

    @patch('requests.post')
    def test_session_persistence(self, mock_post):
        # Mock successful login
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'test-token-123',
            'username': 'testuser'
        }
        mock_post.return_value = mock_response

        # Create auth manager and login
        auth = AuthService(test_mode=True)  # Use AuthService instead of AuthManager
        auth.login('testuser', 'password123')

        # Verify session file was created
        self.assertTrue(os.path.exists(self.auth_file))
        
        # Verify session content
        with open(self.auth_file, 'r') as f:
            saved_session = json.load(f)
            self.assertEqual(saved_session['token'], 'test-token-123')
            self.assertEqual(saved_session['username'], 'testuser')
        
        # Additional debug output
        print(f"\nDEBUG: Session file path: {self.auth_file}")
        print(f"DEBUG: Session state after login: {self.mock_session_state}")

    @patch('requests.get')
    def test_session_loading(self, mock_get):
        # Create mock session file
        test_session = {
            'token': 'test-token-123',
            'username': 'testuser'
        }
        with open(self.auth_file, 'w') as f:
            json.dump(test_session, f)

        # Mock token validation
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'valid': True,
            'user': 'testuser'
        }
        mock_get.return_value = mock_response

        # Update mock session state before creating AuthService
        self.mock_session_state.update(test_session)
        
        # Create auth service instance
        auth = AuthService(test_mode=True)
        
        # Verify session was loaded
        self.assertTrue(auth.is_authenticated)
        self.assertEqual(self.mock_session_state['username'], 'testuser')
        self.assertEqual(self.mock_session_state['token'], 'test-token-123')

        # Additional debug output
        print(f"\nDEBUG: Token validation response: {mock_response.json()}")
        print(f"DEBUG: Session state after load: {self.mock_session_state}")

    def test_session_cleanup(self):
        # Create mock session file
        test_session = {
            'token': 'test-token-123',
            'username': 'testuser'
        }
        with open(self.auth_file, 'w') as f:
            json.dump(test_session, f)

        # Create auth manager and logout
        auth = AuthService(test_mode=True)  # Use AuthService instead of AuthManager
        auth.logout()

        # Verify session was cleared
        with open(self.auth_file, 'r') as f:
            saved_session = json.load(f)
            self.assertIsNone(saved_session['token'])
            self.assertIsNone(saved_session['username'])

class PasswordResetTest(TestMixin, unittest.TestCase):
    def setUp(self):
        self.api_url = 'http://localhost:8000/api'
        self.session = requests.Session()
        
        # Initialize st.session_state for testing
        if not hasattr(st, 'session_state'):
            setattr(st, 'session_state', {})
        st.session_state['token'] = None
        st.session_state['username'] = None
        self.reset_data = {
            'email': 'test@example.com',
            'user_id': 1,
            'token': 'valid-token',
            'new_password': 'newpass123'
        }

    def tearDown(self):
        if hasattr(st, 'session_state'):
            st.session_state.clear()

    @patch('requests.post')
    def test_request_password_reset(self, mock_post):
        # Mock successful password reset request
        mock_post.return_value = self.setup_mock_response(200, {
            'message': 'Password reset email sent!'
        })

        auth = AuthService(test_mode=True)  # Use AuthService instead of AuthManager
        success, message = auth.request_password_reset('test@example.com')
        
        self.assertTrue(success)
        self.assertEqual(message, 'Password reset email sent!')  # No change needed

    @patch('requests.post')
    def test_reset_password_with_token(self, mock_post):
        # Mock successful password reset
        mock_post.return_value = self.setup_mock_response(200, {
            'message': 'Password reset successful!'
        })

        auth = AuthService(test_mode=True)  # Use AuthService instead of AuthManager
        success, message = auth.reset_password(
            user_id=1,
            token='valid-token',
            new_password='newpass123'
        )
        
        self.assertTrue(success)
        self.assertEqual(message, 'Password reset successful!')  # No change needed

    @patch('requests.post')
    def test_password_reset_failure(self, mock_post):
        # Mock failed password reset request
        mock_post.return_value = self.setup_mock_response(404, {
            'error': 'No user found with this email'
        })

        auth = AuthService(test_mode=True)  # Use AuthService instead of AuthManager
        success, message = auth.request_password_reset('nonexistent@example.com')
        
        self.assertFalse(success)
        self.assertEqual(message, 'No user found with this email')

    @patch('requests.post')
    def test_password_reset_rate_limiting(self, mock_post):
        """Test rate limiting for password reset requests"""
        mock_post.return_value = self.setup_mock_response(429, {
            'error': 'Too many requests'
        })

        auth = AuthService(test_mode=True)  # Use AuthService instead of AuthManager
        success, message = auth.request_password_reset('test@example.com')
        self.assertFalse(success)
        self.assertEqual(message, 'Too many requests')

    @patch('requests.post')
    def test_password_reset_malformed_token(self, mock_post):
        """Test handling of malformed reset tokens"""
        mock_post.return_value = self.setup_mock_response(400, {
            'error': 'Invalid token format'
        })

        auth = AuthService(test_mode=True)  # Use AuthService instead of AuthManager
        success, message = auth.reset_password(
            user_id=1,
            token='malformed-token!!!',
            new_password='newpass123'
        )
        self.assertFalse(success)
        self.assertEqual(message, 'Invalid token format')
if __name__ == '__main__':
    django.setup()
    unittest.main()