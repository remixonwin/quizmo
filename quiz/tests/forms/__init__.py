"""
Form tests package.
"""
from .test_quiz import QuizFormTests
from .test_question import QuestionFormTests
from .test_choice import ChoiceFormTests

__all__ = [
    'QuizFormTests',
    'QuestionFormTests',
    'ChoiceFormTests',
]
