"""
Tests for help views.
"""
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from quiz.tests.base import QuizTestCase
from quiz.views.help_views import QuickStartView, StudyMaterialsView, HelpView, FAQView, HelpSearchView
from django.contrib.auth.models import User

class HelpViewsTest(QuizTestCase):
    """Test help views."""

    def setUp(self):
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_help_view(self):
        """Test the main help view"""
        response = self.client.get(reverse('quiz:help'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/help.html')
        self.assertContains(response, 'Help Center')

    def test_quick_start_view(self):
        """Test the Quick Start guide view"""
        response = self.client.get(reverse('quiz:help_quick_start'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/quick_start.html')
        
        # Check if quick start content is displayed
        quick_start = response.context['quick_start_guide']
        for guide in quick_start:
            self.assertContains(response, guide['title'])
            self.assertContains(response, guide['description'])

    def test_study_materials_view(self):
        """Test the Study Materials view"""
        response = self.client.get(reverse('quiz:help_study_materials'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/study_materials.html')
        
        # Check if study materials are displayed
        study_materials = response.context['study_materials']
        for material in study_materials:
            self.assertContains(response, material['title'])
            self.assertContains(response, material['description'])
            if 'link' in material:
                self.assertContains(response, material['link'])
        
        # Check if study tips are displayed
        study_tips = response.context['study_tips']
        for tip in study_tips:
            self.assertContains(response, tip['title'])
            self.assertContains(response, tip['description'])

    def test_faq_view(self):
        """Test the FAQ view"""
        response = self.client.get(reverse('quiz:help_faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/faq.html')
        
        # Check if FAQ content is displayed
        faq_categories = response.context['faq_categories']
        for category in faq_categories:
            self.assertContains(response, category['category'])
            for faq in category['faqs']:
                self.assertContains(response, faq['question'])
                self.assertContains(response, faq['answer'])

    def test_help_search_view(self):
        """Test the help search functionality"""
        # Test search with valid term
        response = self.client.get(
            reverse('quiz:help_search'),
            {'q': 'Minnesota'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/search_results.html')
        self.assertContains(response, 'Search Results')

        # Test empty search
        response = self.client.get(
            reverse('quiz:help_search'),
            {'q': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a search term')

    def test_help_views_require_login(self):
        """Test that help views are public"""
        # List of help URLs to test
        help_urls = [
            reverse('quiz:help'),
            reverse('quiz:help_quick_start'),
            reverse('quiz:help_study_materials'),
            reverse('quiz:help_faq'),
            reverse('quiz:help_search')
        ]
        
        for url in help_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

class HelpContentTest(QuizTestCase):
    """Test help content."""

    def test_help_content_minnesota_specific(self):
        """Test that help content is Minnesota DMV specific"""
        # Get quick start content
        response = self.client.get(reverse('quiz:help_quick_start'))
        quick_start = response.context['quick_start_guide']
        quick_start_text = str(quick_start)
        self.assertIn('Minnesota', quick_start_text)
        
        # Get study materials content
        response = self.client.get(reverse('quiz:help_study_materials'))
        study_materials = response.context['study_materials']
        study_materials_text = str(study_materials)
        self.assertIn('Minnesota', study_materials_text)
        
        # Check study tips
        study_tips = response.context['study_tips']
        study_tips_text = str(study_tips)
        self.assertIn('Minnesota', study_tips_text)

    def test_help_content_structure(self):
        """Test that help content has correct structure"""
        # Test Quick Start guide structure
        response = self.client.get(reverse('quiz:help_quick_start'))
        quick_start = response.context['quick_start_guide']
        self.assertIsInstance(quick_start, list)
        for guide in quick_start:
            self.assertIn('title', guide)
            self.assertIn('description', guide)
        
        # Test Study Materials structure
        response = self.client.get(reverse('quiz:help_study_materials'))
        study_materials = response.context['study_materials']
        self.assertIsInstance(study_materials, list)
        for material in study_materials:
            self.assertIn('title', material)
            self.assertIn('description', material)
            if 'link' in material:
                self.assertIsInstance(material['link'], str)
        
        # Test Study Tips structure
        study_tips = response.context['study_tips']
        self.assertIsInstance(study_tips, list)
        for tip in study_tips:
            self.assertIn('title', tip)
            self.assertIn('description', tip)
        
        # Test FAQs structure
        response = self.client.get(reverse('quiz:help_faq'))
        faq_categories = response.context['faq_categories']
        self.assertIsInstance(faq_categories, list)
        for category in faq_categories:
            self.assertIn('category', category)
            self.assertIn('faqs', category)
            self.assertIsInstance(category['faqs'], list)
            for faq in category['faqs']:
                self.assertIn('question', faq)
                self.assertIn('answer', faq)
