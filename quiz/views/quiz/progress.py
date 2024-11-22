"""
Quiz progress view implemented with functional programming patterns.
"""
from typing import Dict, List, Optional, Any
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from django.core.cache import cache
from ...models import Quiz, QuizAttempt
from ...utils.functional import memoize, pipe, compose, safe_get
from .base import QuizViewMixin

class QuizProgressView(LoginRequiredMixin, QuizViewMixin, TemplateView):
    """View for displaying user's quiz progress."""
    
    template_name = 'quiz/progress.html'
    
    def get_context_data(self, **kwargs):
        """Get context data for template."""
        context = super().get_context_data(**kwargs)
        
        # Get user's attempts
        attempts = QuizAttempt.objects.filter(
            user=self.request.user
        ).select_related('quiz')
        
        # Calculate statistics
        stats = self._calculate_statistics(attempts)
        
        context.update({
            'attempts': attempts,
            'stats': stats,
            'recent_attempts': attempts.order_by('-created_at')[:5],
            'total_attempts': attempts.count(),
            'total_quizzes': Quiz.objects.filter(
                attempts__user=self.request.user
            ).distinct().count()
        })
        
        return context
    
    @memoize
    def _calculate_statistics(self, attempts) -> Dict[str, Any]:
        """Calculate user statistics."""
        if not attempts:
            return {
                'average_score': 0,
                'total_correct': 0,
                'total_questions': 0,
                'completion_rate': 0,
                'pass_rate': 0,
                'average_time': 0
            }
        
        completed_attempts = attempts.filter(completed_at__isnull=False)
        total_completed = completed_attempts.count()
        
        if not total_completed:
            return {
                'average_score': 0,
                'total_correct': 0,
                'total_questions': 0,
                'completion_rate': 0,
                'pass_rate': 0,
                'average_time': 0
            }
        
        # Calculate statistics
        stats = completed_attempts.aggregate(
            average_score=Avg('score'),
            total_correct=Count('answers', filter=Q(answers__choice__is_correct=True)),
            total_questions=Count('answers'),
            pass_count=Count('pk', filter=Q(score__gte=F('quiz__passing_score')))
        )
        
        # Calculate rates
        stats['completion_rate'] = (total_completed / attempts.count()) * 100
        stats['pass_rate'] = (stats['pass_count'] / total_completed) * 100
        
        # Calculate average time
        total_time = sum(
            (attempt.completed_at - attempt.started_at).total_seconds()
            for attempt in completed_attempts
            if attempt.completed_at and attempt.started_at
        )
        stats['average_time'] = total_time / total_completed if total_completed else 0
        
        return stats
