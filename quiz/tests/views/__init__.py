"""
Quiz views test package.
"""
from .test_basic_views import BasicViewTests
from .test_auth import AuthViewTests
from .test_progress import ProgressViewTests
from .test_api import APIViewTests
from .test_scoring import QuizScoringViewTests

__all__ = [
    'BasicViewTests',
    'AuthViewTests',
    'ProgressViewTests',
    'APIViewTests',
    'QuizScoringViewTests',
]
