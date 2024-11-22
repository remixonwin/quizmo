"""
Views for quiz application.
"""
from .quiz_views import (
    QuizListView, QuizDetailView, QuizStartView,
    QuizSubmitView, QuizResultsView
)
from .help_views import HelpView, FAQView
from .auth_views import register_view as register

__all__ = [
    'QuizListView', 'QuizDetailView', 'QuizStartView',
    'QuizSubmitView', 'QuizResultsView',
    'HelpView', 'FAQView',
    'register'
]
