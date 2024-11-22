"""Tests for the help service module."""
import pytest
from django.core.cache import cache
from django.test import override_settings
from quiz.services.help_service import (
    HelpService,
    HelpServiceError,
    InvalidQueryError,
    ContentNotFoundError,
)

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache.clear()
    yield
    cache.clear()

@pytest.mark.django_db
class TestHelpService:
    """Test cases for HelpService class."""

    def test_get_study_tips(self):
        """Test getting study tips."""
        tips = HelpService.get_study_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0
        for tip in tips:
            assert 'title' in tip
            assert 'description' in tip
            assert isinstance(tip['title'], str)
            assert isinstance(tip['description'], str)

    def test_get_study_tips_caching(self):
        """Test study tips are properly cached."""
        # First call should cache the result
        tips1 = HelpService.get_study_tips()
        cache_key = f"{HelpService.CACHE_PREFIX}_study_tips"
        assert cache.get(cache_key) == tips1

        # Second call should use cached result
        tips2 = HelpService.get_study_tips()
        assert tips2 == tips1

    @override_settings(CONTACT_EMAIL='test@example.com')
    def test_get_contact_info(self):
        """Test getting contact information."""
        info = HelpService.get_contact_info()
        assert isinstance(info, dict)
        assert 'email' in info
        assert info['email'] == 'test@example.com'
        assert 'hours' in info
        assert 'response_time' in info

    def test_get_contact_info_caching(self):
        """Test contact info is properly cached."""
        info1 = HelpService.get_contact_info()
        cache_key = f"{HelpService.CACHE_PREFIX}_contact_info"
        assert cache.get(cache_key) == info1

        info2 = HelpService.get_contact_info()
        assert info2 == info1

    @pytest.mark.parametrize('query', [
        'test',
        'study',
        'practice',
        'manual',
        'sign',
    ])
    def test_search_help_valid_queries(self, query):
        """Test search with valid queries."""
        results = HelpService.search_help(query)
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, dict)
            assert 'type' in result
            assert result['type'] in ['section', 'faq', 'material']

    @pytest.mark.parametrize('query', [
        '',  # Too short
        'a',  # Too short
        'a' * 101,  # Too long
    ])
    def test_search_help_invalid_queries(self, query):
        """Test search with invalid queries."""
        with pytest.raises(InvalidQueryError):
            HelpService.search_help(query)

    @override_settings(HELP_FAQS=[
        {
            'category': 'Test',
            'questions': [
                {
                    'question': 'Test question?',
                    'answer': 'Test answer'
                }
            ]
        }
    ])
    def test_search_help_faq_results(self):
        """Test search returns FAQ results."""
        results = HelpService.search_help('test')
        faq_results = [r for r in results if r['type'] == 'faq']
        assert len(faq_results) > 0
        for result in faq_results:
            assert 'category' in result
            assert 'question' in result
            assert 'answer' in result

    @override_settings(HELP_STUDY_MATERIALS=[
        {
            'title': 'Test Material',
            'description': 'Test description',
            'link': 'https://example.com'
        }
    ])
    def test_search_help_material_results(self):
        """Test search returns study material results."""
        results = HelpService.search_help('test')
        material_results = [r for r in results if r['type'] == 'material']
        assert len(material_results) > 0
        for result in material_results:
            assert 'title' in result
            assert 'description' in result
            assert 'link' in result
