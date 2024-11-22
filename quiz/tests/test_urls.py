"""
Test URL configuration.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.test import TestCase
from django.urls import reverse, resolve
from quiz.views.help_views import HelpView, FAQView
from quiz.views.quiz_views import QuizListView, QuizStartView, QuizSubmitView, QuizResultsView
from quiz.views.auth_views import register_view

# Include quiz URLs with namespace
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('quiz.urls', 'quiz'), namespace='quiz')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='quiz:quiz_list'), name='logout'),
    path('accounts/register/', register_view, name='register'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


class TestUrls(TestCase):
    """Test URL routing."""

    def test_help_page_url_resolves(self):
        """Test that help page URL resolves to the correct view."""
        url = reverse('quiz:help')
        self.assertEqual(resolve(url).func.view_class, HelpView)

    def test_faq_page_url_resolves(self):
        """Test that FAQ page URL resolves to the correct view."""
        url = reverse('quiz:help_faq')
        self.assertEqual(resolve(url).func.view_class, FAQView)

    def test_quiz_list_url_resolves(self):
        """Test that quiz list URL resolves to the correct view."""
        url = reverse('quiz:quiz_list')
        self.assertEqual(resolve(url).func.view_class, QuizListView)

    def test_quiz_start_url_resolves(self):
        """Test that quiz start URL resolves to the correct view."""
        url = reverse('quiz:start_quiz', args=[1])
        self.assertEqual(resolve(url).func.view_class, QuizStartView)

    def test_quiz_submit_url_resolves(self):
        """Test that quiz submit URL resolves to the correct view."""
        url = reverse('quiz:quiz_submit', args=[1])
        self.assertEqual(resolve(url).func.view_class, QuizSubmitView)

    def test_quiz_results_url_resolves(self):
        """Test that quiz results URL resolves to the correct view."""
        url = reverse('quiz:quiz_results', args=[1])
        self.assertEqual(resolve(url).func.view_class, QuizResultsView)
