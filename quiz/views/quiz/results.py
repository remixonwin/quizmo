"""
Quiz results view.
"""
from typing import Any, Dict
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Prefetch, QuerySet, Q
from django.utils import timezone
from django.http import HttpRequest, Http404
from django.core.cache import cache
from django.db import models
from .base import QuizViewMixin
from ...models import QuizAttempt, QuizAnswer, Question, Choice
import logging

logger = logging.getLogger(__name__)

class QuizResultsView(LoginRequiredMixin, QuizViewMixin, DetailView):
    """Display quiz results."""
    template_name = 'quiz/quiz_results.html'
    context_object_name = 'attempt'
    
    def get_queryset(self) -> QuerySet:
        """Get quiz attempt with related data."""
        return QuizAttempt.objects.select_related(
            'quiz',
            'user'
        ).prefetch_related(
            Prefetch(
                'answers',
                queryset=QuizAnswer.objects.select_related(
                    'question',
                    'choice'
                ).prefetch_related(
                    'question__choices'
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
        """Get quiz attempt by ID."""
        if queryset is None:
            queryset = self.get_queryset()
        
        # Get ID from URL
        pk = self.kwargs.get('pk')
        
        # Try to find attempt by ID first
        attempt = queryset.filter(id=pk).first()
        
        # If not found, try to find most recent attempt for quiz ID
        if attempt is None:
            attempt = queryset.filter(quiz_id=pk).order_by('-completed_at').first()
        
        if attempt is None:
            raise Http404("No quiz attempt found")
            
        return attempt
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add score and related data to context."""
        context = super().get_context_data(**kwargs)
        attempt = self.object
        
        # Get score from attempt
        score = attempt.score or 0
        passing_score = attempt.quiz.passing_score
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
