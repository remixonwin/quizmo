"""
Test security features of the authentication system.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.messages import get_messages
from ...settings.auth import (
    MAX_LOGIN_ATTEMPTS,
    RATE_LIMIT_ATTEMPTS,
    LOGIN_ATTEMPTS_TIMEOUT,
    ACCOUNT_LOCKOUT_DURATION,
    ACCOUNT_LOCKED_MESSAGE,
)

class TestAuthenticationSecurity(TestCase):
    """Test authentication security features."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.login_url = reverse('quiz:login')
        self.password_reset_url = reverse('quiz:password_reset')
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()

    def test_brute_force_protection(self):
        """Test brute force protection by attempting multiple failed logins."""
        for _ in range(MAX_LOGIN_ATTEMPTS + 1):
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpass'
            })

        self.assertEqual(response.status_code, 429)  # Too Many Requests
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(ACCOUNT_LOCKED_MESSAGE in str(m) for m in messages))

    def test_password_complexity(self):
        """Test password complexity requirements."""
        response = self.client.post(reverse('quiz:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'weak',  # Too short and simple
            'password2': 'weak'
        })

        self.assertEqual(response.status_code, 200)  # Form should not submit
        form = response.context['form']
        self.assertTrue(form.errors.get('password1'))
        self.assertIn('This password is too short', form.errors['password1'][0])

    def test_rate_limiting(self):
        """Test rate limiting for login attempts."""
        for _ in range(RATE_LIMIT_ATTEMPTS + 1):
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpass'
            })

        self.assertEqual(response.status_code, 429)  # Too Many Requests

    def test_secure_password_reset(self):
        """Test security of password reset process."""
        # Test with non-existent email
        response = self.client.post(self.password_reset_url, {
            'email': 'nonexistent@example.com'
        })
        self.assertEqual(response.status_code, 200)  # Should not reveal if email exists

        # Test with valid email
        response = self.client.post(self.password_reset_url, {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect to success page
