"""
Test registration functionality.
"""
from django import forms
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.html import escape
from ..settings.auth import (
    REGISTRATION_SUCCESS_MESSAGE,
    EMAIL_VERIFICATION_TIMEOUT,
    EMAIL_VERIFICATION_REQUIRED_MESSAGE,
    INVALID_TOKEN_MESSAGE
)

@override_settings(SETTINGS_MODULE='quiz.settings.test')
class RegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('quiz:register')
        self.login_url = reverse('quiz:login')
        self.test_user_data = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }

    def test_registration_view(self):
        """Test that registration page loads correctly."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/auth/register.html')

    def test_successful_registration(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.test_user_data)
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@gmail.com')
        self.assertFalse(user.is_active)  # User should be inactive until email verification
        
        # Check verification email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['testuser@gmail.com'])

    def test_password_validation(self):
        """Test password validation rules."""
        test_cases = [
            {
                'password': '123',
                'error': 'This password is too short'
            },
            {
                'password': 'password123',
                'error': 'This password is too common'
            },
            {
                'password': '12345678901',
                'error': 'This password is entirely numeric'
            }
        ]

        for test_case in test_cases:
            data = self.test_user_data.copy()
            data['password1'] = test_case['password']
            data['password2'] = test_case['password']
            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['form'].is_valid())
            self.assertIn('password1', response.context['form'].errors)
            self.assertIn(test_case['error'], str(response.context['form'].errors['password1']))

    def test_password_mismatch(self):
        """Test password mismatch validation."""
        data = self.test_user_data.copy()
        data['password2'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, data)
        
        # Form should be invalid and re-render with error
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('password2', response.context['form'].errors)
        self.assertIn(escape("The two password fields didn't match"), str(response.context['form'].errors['password2']))

    def test_duplicate_username(self):
        """Test duplicate username handling."""
        # Create user first
        User.objects.create_user(username='testuser', email='existing@gmail.com', password='ExistingPass123!')
        
        # Try to register with same username
        response = self.client.post(self.register_url, self.test_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('username', response.context['form'].errors)
        self.assertIn('This username already exists', str(response.context['form'].errors['username']))

    def test_duplicate_email(self):
        """Test duplicate email handling."""
        # Create user first
        User.objects.create_user(username='existing', email='testuser@gmail.com', password='ExistingPass123!')
        
        # Try to register with same email
        response = self.client.post(self.register_url, self.test_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('This email address is already in use', str(response.context['form'].errors['email']))

    def test_blacklisted_email_domain(self):
        """Test blacklisted email domain handling."""
        data = self.test_user_data.copy()
        data['email'] = 'test@blacklisted.com'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('This email domain is not allowed', str(response.context['form'].errors['email']))

    def test_email_verification(self):
        """Test email verification process."""
        # Register user
        response = self.client.post(self.register_url, self.test_user_data)
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Get verification email
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        # Extract verification URL from email
        verification_url = [line for line in email.body.split('\n') if 'verify' in line][0].strip()
        
        # Visit verification URL
        response = self.client.get(verification_url)
        self.assertEqual(response.status_code, 302)  # Should redirect after verification
        
        # Check user is now active
        user = User.objects.get(username='testuser')
        self.assertTrue(user.is_active)

    def test_invalid_verification_token(self):
        """Test invalid verification token handling."""
        # Register user
        self.client.post(self.register_url, self.test_user_data)
        user = User.objects.get(username='testuser')
        
        # Try invalid verification URL
        invalid_url = reverse('quiz:verify_email', kwargs={
            'uidb64': 'invalid',
            'token': 'invalid-token'
        })
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # User should still be inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_unverified_user_login(self):
        """Test that unverified users cannot login."""
        # Register but don't verify
        self.client.post(self.register_url, self.test_user_data)
        
        # Try to login
        login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, EMAIL_VERIFICATION_REQUIRED_MESSAGE)

    def test_registration_form_required_fields(self):
        """Test required fields validation."""
        required_fields = ['username', 'email', 'password1', 'password2']
        
        for field in required_fields:
            data = self.test_user_data.copy()
            data[field] = ''  # Empty required field
            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['form'].is_valid())
            self.assertIn(field, response.context['form'].errors)
            self.assertIn('This field is required', str(response.context['form'].errors[field]))
