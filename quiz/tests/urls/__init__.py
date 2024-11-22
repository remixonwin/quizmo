"""
URL tests package.
"""
from .test_help import HelpUrlTests
from .test_quiz import QuizUrlTests
from .test_auth import AuthUrlTests

__all__ = [
    'HelpUrlTests',
    'QuizUrlTests',
    'AuthUrlTests',
]
