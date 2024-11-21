"""
Quiz views package.
"""
from .list import QuizListView
from .detail import QuizDetailView
from .start import QuizStartView
from .take import view as QuizTakeView
from .submit import view as QuizSubmitView
from .results import QuizResultsView

__all__ = [
    'QuizListView',
    'QuizDetailView',
    'QuizStartView',
    'QuizTakeView',
    'QuizSubmitView',
    'QuizResultsView'
]
