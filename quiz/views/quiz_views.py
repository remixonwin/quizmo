"""
Quiz view imports.
"""
from .quiz.list import QuizListView
from .quiz.detail import QuizDetailView
from .quiz.start import QuizStartView
from .quiz.take import view as QuizTakeView
from .quiz.submit import view as QuizSubmitView
from .quiz.results import QuizResultsView

__all__ = [
    'QuizListView',
    'QuizDetailView',
    'QuizStartView',
    'QuizTakeView',
    'QuizSubmitView',
    'QuizResultsView'
]