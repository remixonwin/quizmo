from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_register_user(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 2)

    def test_login_user(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/token/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_validate_token(self):
        token_response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass123'}, format='json')
        token = token_response.data.get('token')
        response = self.client.post('/api/validate-token/', {'token': token}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['valid'])

    def test_password_reset(self):
        data = {'email': 'test@example.com'}
        response = self.client.post('/api/password-reset/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Password reset email sent')

    def test_reset_password(self):
        data = {'email': 'test@example.com'}
        response = self.client.post('/api/reset-password/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Password reset successful')

    def test_register_user_with_existing_username(self):
        data = {
            'username': 'testuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)

    def test_login_user_with_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/token/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)