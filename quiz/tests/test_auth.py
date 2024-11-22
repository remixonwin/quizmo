import pytest
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core import mail
from django.contrib.messages import get_messages
from quiz.forms import CustomUserCreationForm
from .factories import UserFactory

User = get_user_model()

class TestAuthentication(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('quiz:login')
        self.register_url = reverse('quiz:register')
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
        # Test with wrong password
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self._assert_login_failed(response)

        # Test with empty password
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': '',
        })
        self._assert_login_failed(response)

        # Test with very long password
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'a' * 1000,  # Extremely long password
        })
        self._assert_login_failed(response)

        # Test with special characters in password
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': '!@#$%^&*()',
        })
        self._assert_login_failed(response)

        # Verify login still works with correct password after failed attempts
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': self.test_password,
        })
        self.assertRedirects(response, reverse('quiz:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def _assert_login_failed(self, response):
        """Helper method to assert login failure conditions"""
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any('Invalid username or password' in str(m) for m in messages),
            'Expected error message not found in response'
        )

    def test_logout(self):
        """Test user logout"""
        self.client.login(username='testuser', password=self.test_password)
        response = self.client.get(reverse('quiz:logout'))
        self.assertRedirects(response, reverse('quiz:login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('logged out successfully' in str(m) for m in messages))

    def test_logout_post_not_allowed(self):
        """Test that POST requests to logout are not allowed"""
        self.client.login(username='testuser', password=self.test_password)
        response = self.client.post(reverse('quiz:logout'))
        self.assertEqual(response.status_code, 405)

    def test_login_with_email(self):
        """Test that users can login with email"""
        response = self.client.post(self.login_url, {
            'username': self.test_user.email,
            'password': self.test_password,
        })
        self.assertRedirects(response, reverse('quiz:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_case_insensitive_username(self):
        """Test that username is case-insensitive during login"""
        response = self.client.post(self.login_url, {
            'username': self.test_user.username.upper(),
            'password': self.test_password,
        })
        self.assertRedirects(response, reverse('quiz:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_next_parameter(self):
        """Test login with next parameter for redirect"""
        next_url = reverse('quiz:profile')
        response = self.client.post(f"{self.login_url}?next={next_url}", {
            'username': 'testuser',
            'password': self.test_password,
        })
        self.assertRedirects(response, next_url)

class TestRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('quiz:register')
        cache.clear()

    def test_registration_page_loads(self):
        """Test that registration page loads correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/auth/register.html')

    def test_successful_registration(self):
        """Test successful user registration and email verification flow"""
        # Test registration
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        self.assertRedirects(response, reverse('quiz:login'))
        
        # Check user was created but is inactive
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)
        
        # Check verification email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['newuser@example.com'])
        self.assertIn('Verify your email', mail.outbox[0].subject)
        
        # Extract verification URL from email
        email_content = mail.outbox[0].body
        verification_url = [line for line in email_content.split('\n') if 'verify' in line][0].strip()
        
        # Test email verification
        response = self.client.get(verification_url)
        self.assertRedirects(response, reverse('quiz:login'))
        
        # Check user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Test login after verification
        response = self.client.post(reverse('quiz:login'), {
            'username': 'newuser',
            'password': 'securepass123',
        })
        self.assertRedirects(response, reverse('quiz:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_email_verification_required(self):
        """Test that unverified users cannot login"""
        # Register user
        self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        
        # Attempt login before verification
        response = self.client.post(reverse('quiz:login'), {
            'username': 'newuser',
            'password': 'securepass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('verify your email' in str(m).lower() for m in messages))

    def test_invalid_verification_link(self):
        """Test that invalid verification links are handled properly"""
        # Register user
        self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        
        # Test invalid token
        response = self.client.get(reverse('quiz:verify_email', kwargs={
            'uidb64': 'invalid',
            'token': 'invalid'
        }))
        self.assertRedirects(response, reverse('quiz:login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('invalid verification link' in str(m).lower() for m in messages))
        
        # Check user is still inactive
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)

    def test_registration_with_existing_username(self):
        """Test registration failure with existing username"""
        # Create a user first
        User.objects.create_user(username='existinguser', email='existing@example.com', password='password123')
        
        response = self.client.post(self.register_url, {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('username already exists' in str(m).lower() for m in messages))

    def test_registration_with_invalid_email(self):
        """Test registration with invalid email format"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
        form = response.context['form']
        self.assertIn('email', form.errors)

    def test_registration_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
        form = response.context['form']
        self.assertIn('password2', form.errors)

    def test_registration_with_existing_email(self):
        """Test registration with existing email"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        form = response.context['form']
        self.assertIn('email', form.errors)

    def test_invalid_email_format(self):
        """Test registration with invalid email format"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('valid email address' in str(m).lower() for m in messages))

    def test_blacklisted_email_domain(self):
        """Test registration with blacklisted email domain"""
        with self.settings(BLACKLISTED_EMAIL_DOMAINS=['blacklisted.com']):
            response = self.client.post(self.register_url, {
                'username': 'newuser',
                'email': 'test@blacklisted.com',
                'password1': 'securepass123',
                'password2': 'securepass123',
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(User.objects.filter(username='newuser').exists())
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any('domain is not allowed' in str(m).lower() for m in messages))

    def test_expired_verification_link(self):
        """Test expired verification link"""
        # Register a new user
        self.client.post(self.register_url, {
            'username': 'expireduser',
            'email': 'expired@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        
        user = User.objects.get(username='expireduser')
        
        # Generate expired token
        from quiz.utils.tokens import email_verification_token
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        
        # Modify user to invalidate token
        user.last_login = timezone.now()
        user.save()
        
        # Try to verify with expired token
        verify_url = reverse('quiz:verify_email', args=[uid, token])
        response = self.client.get(verify_url)
        
        # Check user is still inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        
        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('expired' in str(m).lower() for m in messages))

class TestPasswordReset(TestCase):
    def setUp(self):
        self.client = Client()
        self.password_reset_url = reverse('quiz:password_reset')
        self.test_user = UserFactory(
            username='testuser',
            email='test@example.com',
        )
        self.test_user.set_password('testpassword123')
        self.test_user.save()

    def test_password_reset_page_loads(self):
        """Test that password reset page loads correctly"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/auth/password_reset.html')

    def test_password_reset_sends_email(self):
        """Test that password reset sends email"""
        response = self.client.post(self.password_reset_url, {
            'email': self.test_user.email,
        })
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.test_user.email])
        self.assertTemplateUsed(response, 'quiz/auth/password_reset_email.html')
        self.assertRedirects(response, reverse('quiz:password_reset_done'))

    def test_password_reset_invalid_email(self):
        """Test password reset with non-existent email"""
        response = self.client.post(self.password_reset_url, {
            'email': 'nonexistent@example.com',
        })
        self.assertEqual(len(mail.outbox), 0)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('This email is not registered' in str(m) for m in messages))

    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        # First request password reset
        self.client.post(self.password_reset_url, {'email': self.test_user.email})
        
        # Get the token and uidb64 from the sent email
        email_content = mail.outbox[0].body
        reset_url = [line for line in email_content.split('\n') if 'reset' in line][0].strip()
        
        # Extract token and uidb64 from URL
        url_parts = reset_url.split('/')
        uidb64 = url_parts[-2]
        token = url_parts[-1]
        
        # Test the confirmation page
        confirm_url = reverse('quiz:password_reset_confirm', kwargs={
            'uidb64': uidb64,
            'token': token
        })
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/auth/password_reset_confirm.html')

        # Test password reset with valid token and password
        new_password = 'NewPassword123!'
        response = self.client.post(confirm_url, {
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertRedirects(response, reverse('quiz:login'))
        
        # Verify the password was changed
        self.assertTrue(
            self.client.login(username=self.test_user.username, password=new_password)
        )

    def test_password_reset_with_invalid_password(self):
        """Test password reset with invalid password"""
        # First request password reset
        self.client.post(self.password_reset_url, {'email': self.test_user.email})
        
        # Get the token and uidb64 from the sent email
        email_content = mail.outbox[0].body
        reset_url = [line for line in email_content.split('\n') if 'reset' in line][0].strip()
        
        # Extract token and uidb64 from URL
        url_parts = reset_url.split('/')
        uidb64 = url_parts[-2]
        token = url_parts[-1]
        
        # Test the confirmation page
        confirm_url = reverse('quiz:password_reset_confirm', kwargs={
            'uidb64': uidb64,
            'token': token
        })
        
        # Test cases for invalid passwords
        test_cases = [
            ('short', 'Password must be at least 8 characters'),
            ('nouppercase123!', 'Password must contain at least one uppercase letter'),
            ('NOLOWERCASE123!', 'Password must contain at least one lowercase letter'),
            ('NoDigits!', 'Password must contain at least one number'),
            ('NoSpecial123', 'Password must contain at least one special character'),
        ]
        
        for password, expected_error in test_cases:
            response = self.client.post(confirm_url, {
                'new_password1': password,
                'new_password2': password,
            })
            self.assertEqual(response.status_code, 200)
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(
                any(expected_error.lower() in str(m).lower() for m in messages),
                f"Expected error '{expected_error}' not found in messages: {messages}"
            )
            
            # Verify the password was not changed
            self.assertFalse(
                self.client.login(username=self.test_user.username, password=password)
            )

    def test_password_reset_invalid_token(self):
        """Test password reset with invalid token"""
        # First request password reset
        self.client.post(self.password_reset_url, {'email': self.test_user.email})
        
        # Test invalid token
        confirm_url = reverse('quiz:password_reset_confirm', kwargs={
            'uidb64': 'invalid',
            'token': 'invalid-token'
        })
        response = self.client.get(confirm_url)
        self.assertRedirects(response, reverse('quiz:login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('invalid' in str(m).lower() for m in messages))
        
        # Verify password was not changed
        self.assertTrue(
            self.client.login(username=self.test_user.username, password='testpassword123')
        )

    def test_password_reset_expired_token(self):
        """Test password reset with expired token"""
        # First request password reset
        self.client.post(self.password_reset_url, {'email': self.test_user.email})
        
        # Get the token and uidb64 from the sent email
        email_content = mail.outbox[0].body
        reset_url = [line for line in email_content.split('\n') if 'reset' in line][0].strip()
        
        # Extract token and uidb64 from URL
        url_parts = reset_url.split('/')
        uidb64 = url_parts[-2]
        token = url_parts[-1]
        
        # Invalidate token by changing password
        self.test_user.set_password('changedpassword123')
        self.test_user.save()
        
        # Test expired token
        confirm_url = reverse('quiz:password_reset_confirm', kwargs={
            'uidb64': uidb64,
            'token': token
        })
        response = self.client.get(confirm_url)
        self.assertRedirects(response, reverse('quiz:login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('expired' in str(m).lower() for m in messages))

class TestAuthenticationSecurity(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('quiz:login')
        self.register_url = reverse('quiz:register')
        self.test_password = 'testpassword123'
        self.test_user = UserFactory(
            username='testuser',
            email='test@example.com',
        )
        self.test_user.set_password(self.test_password)
        self.test_user.save()
        cache.clear()

    def test_brute_force_protection(self):
        """Test protection against brute force attacks"""
        # Attempt multiple failed logins
        for _ in range(6):  # One more than MAX_LOGIN_ATTEMPTS
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpassword',
            })
        
        # Check if the account is temporarily locked
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('account is locked' in str(m).lower() for m in messages))

    def test_secure_password_validation(self):
        """Test password validation rules"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'password',  # Too simple password
            'password2': 'password',
        })
        form = response.context['form']
        self.assertIn('password1', form.errors)
        self.assertTrue(any('password is too common' in str(err).lower() for err in form.errors['password1']))

    def test_rate_limiting_by_ip(self):
        """Test rate limiting by IP address"""
        # First, try to login with correct credentials
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': self.test_password,
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.client.logout()

        # Now try with wrong password multiple times
        for _ in range(6):
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpassword',
            })
        
        # Try again with correct password, should be blocked
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': self.test_password,
        })
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('account is locked' in str(m).lower() for m in messages))

    def test_password_complexity_requirements(self):
        """Test password complexity requirements during registration"""
        test_cases = [
            ('short', 'Password must be at least 8 characters'),
            ('nouppercase123!', 'Password must contain at least one uppercase letter'),
            ('NOLOWERCASE123!', 'Password must contain at least one lowercase letter'),
            ('NoDigits!', 'Password must contain at least one number'),
            ('NoSpecial123', 'Password must contain at least one special character'),
            ('password123!', 'Password must contain at least one uppercase letter'),
            ('PASSWORD123!', 'Password must contain at least one lowercase letter'),
        ]
        
        for password, expected_error in test_cases:
            response = self.client.post(self.register_url, {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': password,
                'password2': password,
            })
            form = response.context['form']
            self.assertIn('password1', form.errors)
            self.assertTrue(
                any(expected_error.lower() in str(err).lower() for err in form.errors['password1']),
                f"Expected error '{expected_error}' not found in form errors: {form.errors['password1']}"
            )
