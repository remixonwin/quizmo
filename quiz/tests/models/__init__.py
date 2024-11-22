"""
Model tests package.
"""
from .test_quiz import QuizModelTests
from .test_question import QuestionModelTests
from .test_choice import ChoiceModelTests
from .test_attempt import QuizAttemptModelTests

__all__ = [
    'QuizModelTests',
    'QuestionModelTests',
    'ChoiceModelTests',
    'QuizAttemptModelTests',
]
