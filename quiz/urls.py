"""
URL configuration for quiz app.
"""
from django.urls import path
from .views.quiz.submit import QuizSubmitView
from .views.quiz_views import (
    QuizListView, QuizDetailView, QuizStartView,
    QuizTakeView, QuizResultsView
)
from .views import HelpView, FAQView, auth_views
from .views.error_handlers import handler403, handler404, handler500
from .views.health import health_check

app_name = 'quiz'

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('', QuizListView.as_view(), name='quiz_list'),
    path('<int:quiz_id>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('<int:quiz_id>/start/', QuizStartView.as_view(), name='start_quiz'),
    path('<int:quiz_id>/take/', QuizTakeView, name='take_quiz'),
    path('<int:quiz_id>/submit/', QuizSubmitView.as_view(), name='quiz_submit'),
    path('<int:quiz_id>/results/', QuizResultsView.as_view(), name='quiz_results'),
    path('help/', HelpView.as_view(), name='help'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('register/', auth_views.register, name='register'),
]

# Error handlers
handler403 = 'quiz.views.error_handlers.handler403'
handler404 = 'quiz.views.error_handlers.handler404'
handler500 = 'quiz.views.error_handlers.handler500'
