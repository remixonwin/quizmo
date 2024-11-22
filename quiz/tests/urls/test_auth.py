"""
Tests for authentication-related URL configuration.
"""
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import views as auth_views
from quiz.views.auth.register import register_view

class AuthUrlTests(TestCase):
    """Test authentication URL routing."""

    def test_login_url_resolves(self):
        """Test that login URL resolves to the correct view."""
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, auth_views.LoginView)

    def test_logout_url_resolves(self):
        """Test that logout URL resolves to the correct view."""
        url = reverse('logout')
        self.assertEqual(resolve(url).func.view_class, auth_views.LogoutView)

    def test_register_url_resolves(self):
        """Test that register URL resolves to the correct view."""
        url = reverse('register')
        self.assertEqual(resolve(url).func, register_view)

    def test_login_url_name(self):
        """Test login URL name generates correct path."""
        url = reverse('login')
        self.assertEqual(url, '/accounts/login/')

    def test_logout_url_name(self):
        """Test logout URL name generates correct path."""
        url = reverse('logout')
        self.assertEqual(url, '/accounts/logout/')

    def test_register_url_name(self):
        """Test register URL name generates correct path."""
        url = reverse('register')
        self.assertEqual(url, '/accounts/register/')
