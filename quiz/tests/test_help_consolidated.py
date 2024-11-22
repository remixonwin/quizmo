"""
Consolidated tests for help-related views and functionality.
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestHelpViews:
    """Test cases for help-related views and functionality."""
    
    def test_help_page_loads(self, authenticated_client):
        """Test that help page loads correctly."""
        response = authenticated_client.get(reverse('quiz:help'))
        assert response.status_code == 200
        assert 'Help Center' in str(response.content)

    def test_help_page_context(self, authenticated_client, help_page_fixture):
        """Test that help page has correct context data."""
        response = authenticated_client.get(reverse('quiz:help'))
        assert response.status_code == 200
        context = response.context
        
        assert context['title'] == help_page_fixture['title']
        assert context['quick_start'] == help_page_fixture['quick_start']
        assert context['study_tips'] == help_page_fixture['study_tips']
        assert context['support_email'] == help_page_fixture['support']['email']
        assert context['support_phone'] == help_page_fixture['support']['phone']

    def test_study_materials(self, authenticated_client, help_page_fixture):
        """Test study materials content."""
        response = authenticated_client.get(reverse('quiz:help_study_materials'))
        assert response.status_code == 200
        for tip in help_page_fixture['study_tips']:
            assert tip in str(response.content)

    def test_quick_start_guide(self, authenticated_client, help_page_fixture):
        """Test quick start guide content."""
        response = authenticated_client.get(reverse('quiz:help_quick_start'))
        assert response.status_code == 200
        for guide in help_page_fixture['quick_start']:
            assert guide['title'] in str(response.content)
            assert guide['description'] in str(response.content)

    def test_faq_page(self, authenticated_client, help_page_fixture):
        """Test FAQ page content."""
        response = authenticated_client.get(reverse('quiz:faq'))
        assert response.status_code == 200
        
        # Check that all FAQs are present
        content = str(response.content)
        for faq in help_page_fixture['faqs']:
            assert faq['question'] in content
            assert faq['answer'] in content

    def test_help_search(self, authenticated_client):
        """Test help search functionality."""
        search_term = 'quiz'
        response = authenticated_client.get(
            reverse('quiz:help_search'),
            {'q': search_term}
        )
        assert response.status_code == 200
        assert 'Search Results' in str(response.content)

    def test_help_contact(self, authenticated_client, help_page_fixture):
        """Test help contact form."""
        response = authenticated_client.post(
            reverse('quiz:help_contact'),
            {
                'subject': 'Test Subject',
                'message': 'Test Message',
                'email': help_page_fixture['support']['email']
            }
        )
        assert response.status_code == 302  # Redirect after successful submission
        assert 'Thank you for your message' in str(response.wsgi_request._messages)
