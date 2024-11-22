from django.test import TestCase, Client
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

class HelpTemplatesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_help_base_template(self):
        """Test the help base template structure"""
        response = self.client.get(reverse('quiz:help'))
        self.assertTemplateUsed(response, 'quiz/help/help_base.html')
        
        # Check for common elements
        self.assertContains(response, 'Help Center')
        self.assertContains(response, 'Minnesota DMV Practice Quiz')
        self.assertContains(response, 'navigation')
        self.assertContains(response, 'breadcrumb')

    def test_faq_template_structure(self):
        """Test the FAQ template structure and dynamic content"""
        response = self.client.get(reverse('quiz:help_faq'))
        
        # Test accordion structure
        self.assertContains(response, 'accordion')
        self.assertContains(response, 'accordion-item')
        self.assertContains(response, 'accordion-button')
        
        # Test FAQ categories
        for category in settings.HELP_FAQS:
            self.assertContains(response, category['category'])
        
        # Test meta description
        self.assertContains(response, '<meta name="description"')
        self.assertContains(response, 'Find answers to common questions')

    def test_study_materials_template_structure(self):
        """Test the Study Materials template structure"""
        response = self.client.get(reverse('quiz:help_study_materials'))
        
        # Check for Minnesota Driver's Manual section
        self.assertContains(response, 'Minnesota Driver\'s Manual')
        self.assertContains(response, settings.MN_DRIVERS_MANUAL_URL)
        
        # Check for study materials grid
        self.assertContains(response, 'row')
        self.assertContains(response, 'col-md-8')
        self.assertContains(response, 'col-md-4')
        
        # Check for study tips section
        self.assertContains(response, 'Study Tips')
        self.assertContains(response, 'study-tip')
        
        # Check for print button
        self.assertContains(response, 'Print Study Materials')
        self.assertContains(response, 'window.print()')

    def test_print_styles(self):
        """Test that print styles are included in templates"""
        templates = [
            reverse('quiz:help_faq'),
            reverse('quiz:help_study_materials'),
            reverse('quiz:help_quick_start')
        ]
        
        for template_url in templates:
            response = self.client.get(template_url)
            self.assertContains(response, '@media print')
            self.assertContains(response, 'print-friendly')
            # Check that non-printable elements are hidden
            self.assertContains(response, 'd-print-none')

    def test_responsive_design(self):
        """Test that responsive design elements are present"""
        response = self.client.get(reverse('quiz:help'))
        
        # Check for Bootstrap responsive classes
        self.assertContains(response, 'container')
        self.assertContains(response, 'row')
        self.assertContains(response, 'col-md')
        
        # Check for mobile-friendly elements
        self.assertContains(response, 'navbar-toggler')
        self.assertContains(response, 'navbar-collapse')
        self.assertContains(response, 'responsive')

    def test_accessibility_features(self):
        """Test accessibility features in templates"""
        response = self.client.get(reverse('quiz:help'))
        
        # Check for ARIA attributes
        self.assertContains(response, 'aria-label')
        self.assertContains(response, 'aria-current')
        self.assertContains(response, 'role=')
        
        # Check for skip link
        self.assertContains(response, 'skip-link')
        self.assertContains(response, 'Skip to main content')
        
        # Check for semantic HTML
        self.assertContains(response, '<nav')
        self.assertContains(response, '<main')
        self.assertContains(response, '<header')
        
        # Check for proper heading hierarchy
        self.assertContains(response, '<h1')
        self.assertContains(response, '<h2')

    def test_meta_tags(self):
        """Test meta tags in templates"""
        templates = [
            reverse('quiz:help_faq'),
            reverse('quiz:help_study_materials'),
            reverse('quiz:help_quick_start')
        ]
        
        for template_url in templates:
            response = self.client.get(template_url)
            # Check for required meta tags
            self.assertContains(response, '<meta name="description"')
            self.assertContains(response, '<meta name="viewport"')
            self.assertContains(response, '<meta charset="UTF-8"')
            # Check for Minnesota DMV specific content
            self.assertContains(response, 'Minnesota')
            self.assertContains(response, 'DMV')
