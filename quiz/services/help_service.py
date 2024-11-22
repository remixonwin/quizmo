"""
Help service for managing help content and search functionality.
"""
from typing import Dict, List, Any, Optional
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
import logging
import re
from functools import lru_cache
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class HelpServiceError(Exception):
    """Base exception for help service errors."""
    pass

class ContentNotFoundError(HelpServiceError):
    """Raised when requested content is not found."""
    pass

class InvalidQueryError(HelpServiceError):
    """Raised when search query is invalid."""
    pass

class HelpService:
    """Service for managing help content and search functionality."""
    
    CACHE_PREFIX = 'help_content'
    CACHE_TIMEOUT = 3600  # 1 hour
    MIN_QUERY_LENGTH = 2
    MAX_QUERY_LENGTH = 100
    
    @classmethod
    @lru_cache(maxsize=128)
    def get_help_sections(cls) -> List[Dict[str, str]]:
        """Get help center sections with caching."""
        cache_key = f"{cls.CACHE_PREFIX}_sections"
        sections = cache.get(cache_key)
        
        if sections is None:
            try:
                sections = [
                    {
                        'title': 'Quick Start',
                        'description': 'Get started quickly with our platform',
                        'url': reverse('quiz:help_quick_start'),
                        'icon': 'rocket',
                        'tags': ['start', 'begin', 'tutorial', 'guide']
                    },
                    {
                        'title': 'Study Materials',
                        'description': 'Access study materials and resources',
                        'url': reverse('quiz:help_study_materials'),
                        'icon': 'book',
                        'tags': ['study', 'learn', 'materials', 'resources']
                    },
                    {
                        'title': 'FAQ',
                        'description': 'Frequently asked questions',
                        'url': reverse('quiz:help_faq'),
                        'icon': 'question-circle',
                        'tags': ['faq', 'questions', 'answers', 'help']
                    },
                    {
                        'title': 'Contact Support',
                        'description': 'Get in touch with our support team',
                        'url': reverse('quiz:help_contact'),
                        'icon': 'headset',
                        'tags': ['contact', 'support', 'help', 'assistance']
                    }
                ]
                cache.set(cache_key, sections, cls.CACHE_TIMEOUT)
                logger.info("Help sections cached successfully")
            except Exception as e:
                logger.error(f"Error getting help sections: {e}")
                raise HelpServiceError("Unable to retrieve help sections") from e
        
        return sections
    
    @classmethod
    def get_quick_start_guide(cls) -> Dict[str, Any]:
        """Get quick start guide content with error handling."""
        cache_key = f"{cls.CACHE_PREFIX}_quick_start"
        content = cache.get(cache_key)
        
        if content is None:
            try:
                content = {
                    'guide': [
                        {
                            'title': 'Creating an Account',
                            'description': 'Register with your email to start practicing Minnesota DMV tests.',
                            'steps': [
                                'Click "Sign Up" in the top right corner',
                                'Enter your email and create a password',
                                'Verify your email address',
                                'Complete your profile'
                            ],
                            'tags': ['account', 'register', 'signup', 'email']
                        },
                        {
                            'title': 'Taking a Quiz',
                            'description': 'Select a quiz covering Minnesota traffic laws and road signs.',
                            'steps': [
                                'Navigate to the Quiz section',
                                'Choose a quiz category',
                                'Read instructions carefully',
                                'Complete all questions within time limit'
                            ],
                            'tags': ['quiz', 'test', 'practice', 'exam']
                        },
                        {
                            'title': 'Study Materials',
                            'description': 'Access official Minnesota Driver\'s Manual content and practice questions.',
                            'steps': [
                                'Visit the Study Materials section',
                                'Download the Minnesota Driver\'s Manual',
                                'Review road signs guide',
                                'Practice with sample questions'
                            ],
                            'tags': ['study', 'materials', 'manual', 'practice']
                        }
                    ],
                    'faqs': [
                        {
                            'question': 'How do I start?',
                            'answer': 'Create an account and take a practice test.',
                            'tags': ['start', 'begin', 'account']
                        },
                        {
                            'question': 'What do I need?',
                            'answer': 'Just a web browser and internet connection.',
                            'tags': ['requirements', 'browser', 'internet']
                        },
                        {
                            'question': 'Is it free?',
                            'answer': 'Yes, our practice tests are completely free.',
                            'tags': ['free', 'cost', 'price']
                        }
                    ]
                }
                cache.set(cache_key, content, cls.CACHE_TIMEOUT)
                logger.info("Quick start guide cached successfully")
            except Exception as e:
                logger.error(f"Error getting quick start guide: {e}")
                raise HelpServiceError("Unable to retrieve quick start guide") from e
        
        return content
    
    @classmethod
    def search_help_content(cls, query: str) -> List[Dict[str, Any]]:
        """Search through help content with improved relevance and highlighting."""
        if not cls._validate_query(query):
            raise InvalidQueryError("Invalid search query")
        
        results = []
        query = query.lower()
        
        try:
            # Search in FAQs with highlighting
            for category in settings.HELP_FAQS:
                for faq in category['questions']:
                    relevance = cls._calculate_relevance(query, faq['question'], faq['answer'])
                    if relevance > 0:
                        results.append({
                            'title': cls._highlight_text(faq['question'], query),
                            'content': cls._highlight_text(faq['answer'], query),
                            'type': 'FAQ',
                            'url': reverse('quiz:help_faq') + f'#faq-{category["category"].lower()}',
                            'relevance': relevance,
                            'category': category['category']
                        })
            
            # Search in Quick Start Guide
            quick_start = cls.get_quick_start_guide()
            for guide in quick_start['guide']:
                relevance = cls._calculate_relevance(query, guide['title'], guide['description'])
                relevance += cls._calculate_tag_relevance(query, guide.get('tags', []))
                if relevance > 0:
                    results.append({
                        'title': cls._highlight_text(guide['title'], query),
                        'content': cls._highlight_text(guide['description'], query),
                        'type': 'Quick Start',
                        'url': reverse('quiz:help_quick_start'),
                        'relevance': relevance,
                        'steps': guide['steps']
                    })
            
            # Sort results by relevance and add related content
            results.sort(key=lambda x: x['relevance'], reverse=True)
            cls._add_related_content(results)
            
        except Exception as e:
            logger.error(f"Error searching help content: {e}")
            raise HelpServiceError("Error performing help content search") from e
        
        return results
    
    @classmethod
    def _validate_query(cls, query: str) -> bool:
        """Validate search query."""
        if not isinstance(query, str):
            return False
        if len(query) < cls.MIN_QUERY_LENGTH:
            return False
        if len(query) > cls.MAX_QUERY_LENGTH:
            return False
        if not re.match(r'^[\w\s\-\'\"]+$', query):
            return False
        return True
    
    @staticmethod
    def _highlight_text(text: str, query: str) -> str:
        """Highlight search terms in text using HTML."""
        if not query or not text:
            return text
        
        pattern = re.compile(f'({re.escape(query)})', re.IGNORECASE)
        return pattern.sub(r'<mark>\1</mark>', text)
    
    @staticmethod
    def _calculate_relevance(query: str, title: str, content: str) -> float:
        """Calculate search result relevance score with fuzzy matching."""
        relevance = 0.0
        
        # Title matches with fuzzy matching
        title_ratio = SequenceMatcher(None, query, title.lower()).ratio()
        if title_ratio > 0.6:
            relevance += title_ratio * 3.0
        
        # Content matches
        content_ratio = SequenceMatcher(None, query, content.lower()).ratio()
        if content_ratio > 0.4:
            relevance += content_ratio * 1.5
        
        # Exact matches are weighted more heavily
        if query == title.lower():
            relevance += 3.0
        if query in content.lower():
            relevance += 1.0
        
        return relevance
    
    @staticmethod
    def _calculate_tag_relevance(query: str, tags: List[str]) -> float:
        """Calculate relevance based on tags."""
        relevance = 0.0
        for tag in tags:
            if query in tag.lower():
                relevance += 0.5
            elif tag.lower() in query:
                relevance += 0.3
        return relevance
    
    @classmethod
    def _add_related_content(cls, results: List[Dict[str, Any]]) -> None:
        """Add related content suggestions to search results."""
        if not results:
            return
        
        for result in results:
            related = []
            result_type = result['type']
            
            # Find related content based on type and tags
            if result_type == 'FAQ':
                # Add related FAQs from same category
                category = result.get('category')
                if category:
                    for r in results:
                        if (r['type'] == 'FAQ' and 
                            r['category'] == category and 
                            r != result):
                            related.append({
                                'title': r['title'],
                                'url': r['url'],
                                'type': 'FAQ'
                            })
            
            elif result_type == 'Quick Start':
                # Add related study materials and FAQs
                for r in results:
                    if r != result and r['type'] in ['FAQ', 'Quick Start']:
                        related.append({
                            'title': r['title'],
                            'url': r['url'],
                            'type': r['type']
                        })
            
            # Limit related content to top 3
            result['related'] = related[:3]
