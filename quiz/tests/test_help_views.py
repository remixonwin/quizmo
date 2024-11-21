"""
Tests for help and FAQ views.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class HelpViewTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_help_page_view(self):
        """Test the help page view."""
        response = self.client.get(reverse('quiz:help'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/help.html')
        self.assertContains(response, 'Help Center')
        
        # Test context data
        self.assertIn('quick_start', response.context)
        self.assertIn('faqs', response.context)
        self.assertEqual(response.context['title'], 'Help Center')
        self.assertEqual(response.context['page_title'], 'Help Center')

    def test_help_page_search(self):
        """Test the help page search functionality."""
        response = self.client.get(reverse('quiz:help'), {'search': 'account'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/help.html')
        self.assertContains(response, 'account')

    def test_faq_page_view(self):
        """Test the FAQ page view."""
        response = self.client.get(reverse('quiz:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/help/faq.html')
        self.assertContains(response, 'Frequently Asked Questions')

    def test_help_page_quick_start_content(self):
        """Test that quick start guide content is present."""
        response = self.client.get(reverse('quiz:help'))
        quick_start = response.context['quick_start']
        
        # Verify quick start guide sections
        expected_titles = ['Register/Login', 'Choose a Quiz', 'Take the Quiz', 'Review Results']
        actual_titles = [item['title'] for item in quick_start]
        self.assertEqual(actual_titles, expected_titles)

    def test_help_page_faq_content(self):
        """Test that FAQ content is present."""
        response = self.client.get(reverse('quiz:help'))
        faqs = response.context['faqs']
        
        # Verify FAQ questions exist
        expected_questions = [
            'How do I create an account?',
            'How are quizzes scored?',
            'What is the passing score?',
            'Can I review my answers?'
        ]
        actual_questions = [item['question'] for item in faqs]
        self.assertEqual(actual_questions, expected_questions)

    def test_faq_page_content(self):
        """Test FAQ page specific content."""
        response = self.client.get(reverse('quiz:faq'))
        self.assertEqual(response.context['title'], 'FAQ')
        
        faqs = response.context['faqs']
        self.assertTrue(len(faqs) > 0)
        
        # Test specific FAQ content
        self.assertTrue(any(
            faq['question'] == 'How do I create an account?' 
            for faq in faqs
        ))
        
        # Test FAQ answer content
        self.assertTrue(any(
            'Click the "Register" link' in faq['answer']
            for faq in faqs
        ))

    def test_help_page_security_headers(self):
        """Test security headers are properly set."""
        response = self.client.get(reverse('quiz:help'))
        self.assertEqual(
            response.headers['X-Frame-Options'],
            'DENY'
        )

    def test_faq_page_security_headers(self):
        """Test security headers are properly set for FAQ page."""
        response = self.client.get(reverse('quiz:faq'))
        self.assertEqual(
            response.headers['X-Frame-Options'],
            'DENY'
        )
