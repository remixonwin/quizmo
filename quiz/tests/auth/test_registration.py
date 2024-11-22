import pytest
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from ..factories import UserFactory
from ...settings.auth import (
    EMAIL_VERIFICATION_REQUIRED,
    REGISTRATION_SUCCESS_MESSAGE,
)

User = get_user_model()

class TestRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('quiz:register')
        self.test_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }

    def test_registration_page_loads(self):
        """Test that registration page loads correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/auth/register.html')

    def test_successful_registration(self):
        """Test successful user registration and email verification flow"""
        response = self.client.post(self.register_url, self.test_data)
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertRedirects(response, reverse('quiz:login'))
        
        # Check user was created
        user = User.objects.get(username=self.test_data['username'])
        self.assertFalse(user.is_active)
        
        # Check verification email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('Verify your email', email.subject)
        
        # Extract verification link and verify
        verification_url = [line for line in email.body.split('\n') if 'verify' in line][0].strip()
        response = self.client.get(verification_url)
        self.assertEqual(response.status_code, 302)  # Should redirect after verification
        
        # Check user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_email_verification_required(self):
        """Test that unverified users cannot login"""
        # Register user
        self.client.post(self.register_url, self.test_data)
        
        # Attempt to login
        response = self.client.post(reverse('quiz:login'), {
            'username': self.test_data['username'],
            'password': self.test_data['password1']
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('verify your email' in str(m).lower() for m in messages))

    def test_registration_with_existing_username(self):
        """Test registration failure with existing username"""
        # Create existing user
        UserFactory(username=self.test_data['username'])
        
        response = self.client.post(self.register_url, self.test_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors.get('username'))
        self.assertIn('already exists', form.errors['username'][0])

    def test_registration_with_existing_email(self):
        """Test registration with existing email"""
        # Create existing user
        UserFactory(email=self.test_data['email'])
        
        response = self.client.post(self.register_url, self.test_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors.get('email'))
        self.assertIn('This email address is already in use', form.errors['email'][0])

    def test_registration_with_invalid_email(self):
        """Test registration with invalid email format"""
        self.test_data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, self.test_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors.get('email'))
        self.assertIn('Enter a valid email address', form.errors['email'][0])

    def test_invalid_verification_link(self):
        """Test that invalid verification links are handled properly"""
        # Register user first
        self.client.post(self.register_url, self.test_data)
        
        # Try invalid verification link
        invalid_url = reverse('quiz:verify_email', kwargs={
            'uidb64': 'invalid-uid',
            'token': 'invalid-token'
        })
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 400)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('invalid verification link' in str(m).lower() for m in messages))
