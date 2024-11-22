"""
Tests for help-related URL configuration.
"""
from django.test import TestCase
from django.urls import reverse, resolve
from quiz.views.help_views import HelpView, FAQView

class HelpUrlTests(TestCase):
    """Test help URL routing."""

    def test_help_page_url_resolves(self):
        """Test that help page URL resolves to the correct view."""
        url = reverse('quiz:help')
        self.assertEqual(resolve(url).func.view_class, HelpView)

    def test_faq_page_url_resolves(self):
        """Test that FAQ page URL resolves to the correct view."""
        url = reverse('quiz:help_faq')
        self.assertEqual(resolve(url).func.view_class, FAQView)

    def test_help_url_name(self):
        """Test help URL name generates correct path."""
        url = reverse('quiz:help')
        self.assertEqual(url, '/help/')

    def test_faq_url_name(self):
        """Test FAQ URL name generates correct path."""
        url = reverse('quiz:help_faq')
        self.assertEqual(url, '/help/faq/')
