"""
Base classes for quiz views.
"""
from typing import Any, Dict, Optional
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpRequest
from ..models import Quiz, QuizAttempt

class QuizBaseView(LoginRequiredMixin):
    """Base view for quiz functionality."""
    
    def get_quiz_cache_key(self, quiz_id: int) -> str:
        """Get cache key for quiz data."""
        return f'quiz_detail_{quiz_id}'
    
    def get_attempt_cache_key(self, quiz_id: int, user_id: int) -> str:
        """Get cache key for quiz attempt data."""
        return f'quiz_attempt_{quiz_id}_{user_id}'

class QuizQuerySetMixin:
    """Mixin for quiz queryset optimization."""
    
    def get_quiz_queryset(self) -> QuerySet:
        """Get optimized quiz queryset."""
        return Quiz.objects.filter(is_active=True).order_by('-created_at')
    
    def get_quiz_detail_queryset(self, quiz_id: int) -> QuerySet:
        """Get optimized quiz detail queryset."""
        return Quiz.objects.prefetch_related(
            'questions__choices'
        ).filter(id=quiz_id, is_active=True)

class QuizAttemptMixin:
    """Mixin for quiz attempt functionality."""
    
    def get_active_attempt(self, request: HttpRequest, quiz_id: Optional[int] = None) -> Optional[QuizAttempt]:
        """Get user's active quiz attempt."""
        attempts = QuizAttempt.objects.filter(
            user=request.user,
            completed_at__isnull=True
        ).select_related('quiz')
        
        if quiz_id:
            attempts = attempts.filter(quiz_id=quiz_id)
            
        return attempts.first()
    
    def handle_timeout(self, attempt: QuizAttempt) -> bool:
        """Handle quiz attempt timeout."""
        if attempt.is_timed_out:
            attempt.submit()
            return True
        return False
