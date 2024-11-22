"""
Base test classes package.
"""
from .media import MediaTestCase
from .auth import AuthTestCase
from .quiz import QuizTestCase
from .question import QuestionTestCase

__all__ = [
    'MediaTestCase',
    'AuthTestCase',
    'QuizTestCase',
    'QuestionTestCase',
]
