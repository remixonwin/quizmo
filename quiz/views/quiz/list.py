"""
Quiz list view with functional programming patterns.
"""
from typing import Dict, Any, Optional
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from ...models import Quiz, Question
from .base import QuizViewMixin, QuizQuerySetMixin
import logging

logger = logging.getLogger(__name__)

class QuizListView(LoginRequiredMixin, QuizViewMixin, QuizQuerySetMixin, ListView):
    """Display list of available quizzes."""
    model = Quiz
    template_name = 'quiz/quiz_list.html'
    context_object_name = 'quizzes'
    paginate_by = 12
    login_url = '/accounts/login/'

    def get_paginate_by(self, queryset):
        """Get custom page size from request or settings."""
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        """Get only the Minnesota Road Signs quiz."""
        return self.get_quiz_queryset().filter(
            title__icontains='Minnesota Road Signs'
        ).prefetch_related('questions')[:1]

    def get_context_data(self, **kwargs):
        """Add pagination context and user-specific quiz stats."""
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = False  # Only showing one quiz
        if self.request.user.is_authenticated:
            for quiz in context['quizzes']:
                quiz.user_attempts = quiz.get_user_attempts(self.request.user)
                quiz.best_score = quiz.get_best_score(self.request.user)
        return context
