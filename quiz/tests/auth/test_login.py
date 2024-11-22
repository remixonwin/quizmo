import pytest
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.cache import cache
from ..factories import UserFactory
from ...settings.auth import (
    LOGIN_ERROR_MESSAGE,
    EMAIL_VERIFICATION_REQUIRED,
    EMAIL_VERIFICATION_REQUIRED_MESSAGE,
)

User = get_user_model()

class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('quiz:login')
        self.test_password = 'testpassword123'
        self.test_user = UserFactory(
            username='testuser',
            email='test@example.com',
        )
        self.test_user.set_password(self.test_password)
        self.test_user.save()
        # Clear login attempts cache
        cache.clear()

    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/auth/login.html')

    def test_successful_login(self):
        """Test successful user login"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': self.test_password,
        })
        self.assertRedirects(response, reverse('quiz:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Welcome back' in str(m) for m in messages))

    def test_failed_login_wrong_password(self):
        """Test login failure scenarios with wrong password"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(LOGIN_ERROR_MESSAGE in str(m) for m in messages))

    def test_failed_login_nonexistent_user(self):
        """Test login failure with non-existent user"""
        response = self.client.post(self.login_url, {
            'username': 'nonexistentuser',
            'password': self.test_password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(LOGIN_ERROR_MESSAGE in str(m) for m in messages))

    def test_login_inactive_user(self):
        """Test that inactive users cannot login"""
        # Create an inactive user
        user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@test.com',
            password='testpass123'
        )
        user.is_active = False
        user.save()

        response = self.client.post(self.login_url, {
            'username': 'inactiveuser',
            'password': 'testpass123'
        })

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(EMAIL_VERIFICATION_REQUIRED_MESSAGE in str(m).lower() for m in messages))
