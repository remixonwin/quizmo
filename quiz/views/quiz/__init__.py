"""
Quiz views package.
"""
from .list import QuizListView
from .detail import QuizDetailView
from .start import QuizStartView
from .take import QuizTakeView
from .submit import QuizSubmitView
from .results import QuizResultsView

__all__ = [
    'QuizListView',
    'QuizDetailView',
    'QuizStartView',
    'QuizTakeView',
    'QuizSubmitView',
    'QuizResultsView'
]
