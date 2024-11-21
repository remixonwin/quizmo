"""
Tests for the help page functionality.
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz.tests.test_settings')

import django
django.setup()

from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.conf import settings
from django.test.utils import override_settings


class HelpPageTests(TransactionTestCase):
    """Test cases for help page functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level test data."""
        super().setUpClass()
        # Run migrations
        call_command('migrate', verbosity=0, interactive=False)
        
    def setUp(self):
        """Set up test client and URLs."""
        super().setUp()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.help_url = reverse('quiz:help')
        self.faq_url = reverse('quiz:faq')
        self.quiz_list_url = reverse('quiz:quiz_list')

    def test_help_page_url_exists(self):
        """Test that help page URL exists and returns 200."""
        response = self.client.get(self.help_url)
        self.assertEqual(response.status_code, 200)

    def test_help_page_uses_correct_template(self):
        """Test that help page uses the correct template."""
        response = self.client.get(self.help_url)
        self.assertTemplateUsed(response, 'quiz/help/help.html')  # Updated template path

    def test_help_page_content(self):
        """Test that help page contains expected content."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test section headings exist
        self.assertIn('Quick Start Guide', content)
        self.assertIn('Frequently Asked Questions', content)
        self.assertIn('Study Materials', content)  # Updated section name

        # Test specific content elements
        self.assertIn('Create an Account', content)  # Updated content
        self.assertIn('Choose a Test', content)  # Updated content
        self.assertIn('Take Practice Tests', content)  # Updated content
        self.assertIn('Review Results', content)
        
        # Test FAQ content
        self.assertIn('Minnesota Driver\'s Manual', content)  # Updated content
        self.assertIn('Practice Tests', content)

    def test_help_page_accessible_when_logged_out(self):
        """Test that help page is accessible when not logged in."""
        response = self.client.get(self.help_url)
        self.assertEqual(response.status_code, 200)

    def test_help_page_accessible_when_logged_in(self):
        """Test that help page is accessible when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.help_url)
        self.assertEqual(response.status_code, 200)

    def test_help_link_from_home(self):
        """Test that help page is accessible from home page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.quiz_list_url)
        content = response.content.decode('utf-8')
        
        # Test Help link presence
        self.assertIn('Help', content)
        self.assertIn(reverse('quiz:help'), content)

    def test_navigation_links_present(self):
        """Test that navigation links are present in the template."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test navigation menu items
        self.assertIn('Home', content)
        self.assertIn('Help Center', content)  # Updated content

    def test_help_page_context_data(self):
        """Test that help page view provides correct context data."""
        response = self.client.get(self.help_url)
        self.assertEqual(response.context['title'], 'Help Center')
        self.assertEqual(response.context['page_title'], 'Help Center')
        self.assertTrue('quick_start' in response.context)
        self.assertTrue('faqs' in response.context)
        self.assertTrue('study_materials' in response.context)

    def test_help_page_meta_tags(self):
        """Test that help page has proper meta tags."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test meta tags
        self.assertIn('<title>Help Center - Minnesota DMV Practice Test</title>', content)
        self.assertIn('<meta name="viewport"', content)
        self.assertIn('<meta charset="UTF-8"', content)

    def test_help_page_search(self):
        """Test help page search functionality."""
        response = self.client.get(f'{self.help_url}?search=quiz')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('search_query' in response.context)
        self.assertEqual(response.context['search_query'], 'quiz')

    def test_help_page_security_headers(self):
        """Test that help page has proper security headers."""
        response = self.client.get(self.help_url)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')

    def test_help_page_caching(self):
        """Test help page caching behavior."""
        response = self.client.get(self.help_url)
        self.assertEqual(response['Cache-Control'], 'no-cache, no-store, must-revalidate')
        self.assertEqual(response['Pragma'], 'no-cache')
        self.assertEqual(response['Expires'], '0')

    def test_help_page_breadcrumbs(self):
        """Test help page breadcrumb navigation."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        self.assertIn('Home</a>', content)
        self.assertIn('Help Center', content)

    def test_support_contact_information(self):
        """Test that support contact information is present."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        self.assertIn(settings.CONTACT_EMAIL, content)
        if hasattr(settings, 'SUPPORT_PHONE'):
            self.assertIn(settings.SUPPORT_PHONE, content)

    def test_ui_elements_present(self):
        """Test that all UI elements are present."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        self.assertIn('Quick Start Guide', content)
        self.assertIn('Study Materials', content)
        self.assertIn('Contact Support', content)

    def test_responsive_layout(self):
        """Test that the layout is responsive."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        self.assertIn('class="container', content)
        self.assertIn('class="row', content)
        self.assertIn('class="col-', content)

    def test_help_page_accessibility(self):
        """Test accessibility features."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        self.assertIn('role="main"', content)
        self.assertIn('aria-label', content)
        self.assertIn('aria-current', content)

    def test_help_page_print_styles(self):
        """Test print-specific styles."""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        self.assertIn('@media print', content)
        self.assertIn('print-friendly', content)
