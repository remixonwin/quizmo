"""
Quiz list view with functional programming patterns.
"""
from typing import Dict, Any, Optional
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from .base import QuizViewMixin, QuizQuerySetMixin
import logging

logger = logging.getLogger(__name__)

class QuizListView(LoginRequiredMixin, QuizViewMixin, QuizQuerySetMixin, ListView):
    """Display list of available quizzes."""
    template_name = 'quiz/quiz_list.html'
    context_object_name = 'quizzes'
    paginate_by = 10
    login_url = '/accounts/login/'

    def get_paginate_by(self, queryset):
        """Get custom page size from request or settings."""
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        """Get only the Minnesota Road Signs quiz."""
        return self.get_quiz_queryset().filter(
            title__icontains='Minnesota Road Signs'
        ).annotate(
            question_count=Count('questions')
        ).prefetch_related('questions')[:1]

    def get_context_data(self, **kwargs):
        """Add pagination context."""
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = False  # Only showing one quiz
        return context
