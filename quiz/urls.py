from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('', views.QuizListView.as_view(), name='home'),
    path('help/', views.help_page, name='help'),
    path('register/', views.register, name='register'),
    path('log-client-error/', views.log_client_error, name='log_client_error'),
    path('test-errors/', views.test_error_page, name='test_errors'),
    path('preview/', views.preview_page, name='preview'),
    path('practice/', views.QuizListView.as_view(), name='practice'),
    path('results/', views.quiz_results, name='results'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
]

# Error handlers
handler403 = 'quiz.views.handler403'
handler404 = 'quiz.views.handler404'
handler500 = 'quiz.views.handler500'
