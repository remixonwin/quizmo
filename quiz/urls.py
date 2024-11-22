"""
URL configuration for quiz app.
"""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views.auth.login import login_view
from .views.auth.register import register_view
from .views.auth.verification import verify_email_view
from .views.auth.logout import logout_view
from .views.auth.profile import profile, dashboard
from .views.auth.password import (
    password_reset_view,
    password_reset_confirm_view
)
from .views.auth.privacy import privacy_policy
from .views.quiz import (
    QuizListView, QuizDetailView, QuizTakeView,
    QuizSubmitView, QuizResultsView
)
from .views.quiz.admin import QuizCreateView, QuizEditView, QuizDeleteView
from .views.help_views import (
    HelpView, FAQView, QuickStartView, StudyMaterialsView,
    HelpContactView
)
from .views.error_views import handler403, handler404, handler500
from .views.health import health_check

app_name = 'quiz'

urlpatterns = [
    # Health Check URL
    path('health/', health_check, name='health_check'),
    
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email_view, name='verify_email'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', password_reset_view, name='password_reset'),
    path('password-reset/done/',
        TemplateView.as_view(
            template_name='quiz/auth/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path('password-reset-confirm/<uidb64>/<token>/',
        password_reset_confirm_view,
        name='password_reset_confirm'
    ),
    path('password-reset-complete/',
        TemplateView.as_view(
            template_name='quiz/auth/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    
    # Profile and Dashboard URLs
    path('profile/', profile, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    
    # Quiz URLs
    path('', QuizListView.as_view(), name='quiz_list'),
    path('<int:quiz_id>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('quiz/create/', QuizCreateView.as_view(), name='quiz_create'),
    path('quiz/<int:quiz_id>/edit/', QuizEditView.as_view(), name='quiz_edit'),
    path('quiz/<int:quiz_id>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
    path('<int:quiz_id>/take/', QuizTakeView.as_view(), name='quiz_take'),
    path('<int:quiz_id>/take/submit/', QuizSubmitView.as_view(), name='quiz_submit'),
    path('<int:quiz_id>/results/', QuizResultsView.as_view(), name='quiz_results'),
    
    # Help URLs
    path('help/', HelpView.as_view(), name='help'),
    path('help/quick-start/', QuickStartView.as_view(), name='help_quick_start'),
    path('help/study-materials/', StudyMaterialsView.as_view(), name='help_study_materials'),
    path('help/faq/', FAQView.as_view(), name='help_faq'),
    path('help/contact/', HelpContactView.as_view(), name='help_contact'),
    
    # Legal URLs
    path('privacy/', privacy_policy, name='privacy'),
]

# Error handlers
handler403 = 'quiz.views.error_views.handler403'
handler404 = 'quiz.views.error_views.handler404'
handler500 = 'quiz.views.error_views.handler500'

# Add static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
