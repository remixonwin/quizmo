"""
Quiz results view.
"""
from typing import Any, Dict
from django.views.generic import DetailView
from django.db.models import Prefetch, QuerySet, Count, Q
from django.http import HttpRequest, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db import models
from .base import QuizViewMixin
from ...models import QuizAttempt, UserAnswer, Question, Choice
import logging

logger = logging.getLogger(__name__)

class QuizResultsView(LoginRequiredMixin, QuizViewMixin, DetailView):
    """Display quiz results."""
    template_name = 'quiz/quiz_results.html'
    context_object_name = 'attempt'
    
    def get_queryset(self) -> QuerySet:
        """Get quiz attempt with related data."""
        return QuizAttempt.objects.select_related(
            'quiz'
        ).prefetch_related(
            Prefetch(
                'answers',
                queryset=UserAnswer.objects.select_related(
                    'question',
                    'choice'
                ).prefetch_related(
                    Prefetch(
                        'question__choices',
                        queryset=Choice.objects.filter(is_correct=True),
                        to_attr='correct_choices'
                    )
                ).order_by('question__order')
            )
        ).filter(
            user=self.request.user,
            completed_at__isnull=False
        ).annotate(
            total_questions=Count('quiz__questions', distinct=True),
            correct_answers=Count(
                'answers',
                filter=Q(answers__choice__is_correct=True),
                distinct=True
            )
        )
    
    def get_object(self, queryset: QuerySet = None) -> QuizAttempt:
        """Get most recent completed attempt."""
        if queryset is None:
            queryset = self.get_queryset()
            
        # Check cache first
        cache_key = f'quiz_results_{self.kwargs.get("quiz_id")}_{self.request.user.id}'
        cached_attempt = cache.get(cache_key)
        if cached_attempt:
            return cached_attempt
            
        try:
            attempt = queryset.filter(quiz_id=self.kwargs.get('quiz_id')).latest('completed_at')
            # Cache for 5 minutes
            cache.set(cache_key, attempt, 300)
            return attempt
        except QuizAttempt.DoesNotExist:
            logger.warning(
                f'No completed attempt found for quiz {self.kwargs.get("quiz_id")} '
                f'and user {self.request.user.id}'
            )
            raise Http404('No completed quiz attempt found.')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add score and related data to context."""
        context = super().get_context_data(**kwargs)
        attempt = self.object
        
        # Get score from attempt
        score = attempt.score or 0
        passing_score = attempt.quiz.pass_mark
        passed = score >= passing_score
        
        context.update({
            'quiz': attempt.quiz,
            'score': round(score, 1),
            'correct_answers': attempt.correct_answers,
            'total_questions': attempt.total_questions,
            'passing_score': passing_score,
            'passed': passed,
            'status': 'Passed' if passed else 'Not Passed',
            'page_title': f'Results: {attempt.quiz.title}'
        })
        
        return context
