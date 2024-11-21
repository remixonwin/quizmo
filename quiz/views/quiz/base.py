"""
Base quiz view mixin with functional programming patterns.
"""
from typing import Optional, Any, Dict, TypeVar, Callable
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet
from ...utils.functional import (
    compose, pipe, memoize, safe_get,
    validate_request, time_window
)
from ...models import Quiz, QuizAttempt
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')

class QuizQuerySetMixin:
    """Mixin for quiz queryset operations."""
    
    def get_quiz_queryset(self) -> QuerySet[Quiz]:
        """Get active quiz queryset."""
        return Quiz.objects.filter(
            is_active=True
        ).order_by('-created_at')

class QuizViewMixin:
    """Base mixin for quiz views."""
    
    def get_cached_quiz(self, quiz_id: int) -> Optional[Quiz]:
        """Get quiz from cache."""
        cache_key = f'quiz_{quiz_id}'
        quiz = cache.get(cache_key)
        if not quiz:
            quiz = Quiz.objects.filter(id=quiz_id).first()
            if quiz:
                self.cache_quiz(quiz)
        return quiz
    
    def cache_quiz(self, quiz: Quiz) -> None:
        """Cache quiz data."""
        cache.set(
            f'quiz_{quiz.id}',
            quiz,
            timeout=settings.CACHE_TIMEOUT
        )
    
    def get_active_attempt(self, user, quiz_id: int) -> Optional[QuizAttempt]:
        """Get active quiz attempt."""
        cache_key = f'attempt_{user.id}_{quiz_id}'
        attempt = cache.get(cache_key)
        
        if not attempt:
            attempt = QuizAttempt.objects.filter(
                user=user,
                quiz_id=quiz_id,
                completed_at__isnull=True
            ).first()
            if attempt:
                cache.set(cache_key, attempt, timeout=settings.CACHE_TIMEOUT)
                
        return attempt
    
    def get_or_create_attempt(
        self,
        user,
        quiz_id: int
    ) -> Optional[QuizAttempt]:
        """Get or create quiz attempt."""
        attempt = self.get_active_attempt(user, quiz_id)
        if not attempt:
            quiz = Quiz.objects.filter(id=quiz_id).first()
            if quiz:
                attempt = QuizAttempt.objects.create(
                    user=user,
                    quiz=quiz,
                    started_at=timezone.now(),
                    metadata={
                        'total_points': '0.0',
                        'earned_points': '0.0',
                        'correct_answers': 0,
                        'total_questions': 0,
                        'difficulty_stats': {
                            'easy': {'total': 0, 'correct': 0},
                            'medium': {'total': 0, 'correct': 0},
                            'hard': {'total': 0, 'correct': 0}
                        },
                        'completion_time': 0.0
                    }
                )
                cache_key = f'attempt_{user.id}_{quiz_id}'
                cache.set(cache_key, attempt, timeout=settings.CACHE_TIMEOUT)
                logger.info(f'Created attempt {attempt.id} for quiz {quiz_id}')
        return attempt
    
    def is_quiz_completed(self, user, quiz_id: int) -> bool:
        """Check if quiz is completed."""
        cache_key = f'completed_{user.id}_{quiz_id}'
        completed = cache.get(cache_key)
        
        if completed is None:
            completed = QuizAttempt.objects.filter(
                user=user,
                quiz_id=quiz_id,
                completed_at__isnull=False
            ).exists()
            cache.set(cache_key, completed, timeout=settings.CACHE_TIMEOUT)
            
        return completed
    
    def can_start_quiz(self, user, quiz_id: int) -> bool:
        """Check if user can start quiz."""
        validate = validate_request([
            lambda _: user.is_authenticated,
            lambda _: not self.is_quiz_completed(user, quiz_id),
            lambda _: not self.get_active_attempt(user, quiz_id)
        ])
        return validate(None)
    
    def get_time_limit(self) -> int:
        """Get quiz time limit in minutes."""
        return getattr(settings, 'QUIZ_TIME_LIMIT_MINUTES', 60)
    
    def get_remaining_time(self, attempt: QuizAttempt) -> int:
        """Get remaining time in seconds."""
        if not attempt.started_at:
            return self.get_time_limit() * 60
            
        time_limit = timedelta(minutes=self.get_time_limit())
        time_elapsed = timezone.now() - attempt.started_at
        remaining = max(time_limit - time_elapsed, timedelta(0))
        return int(remaining.total_seconds())
    
    def check_time_limit(
        self,
        attempt: QuizAttempt,
        request: HttpRequest
    ) -> bool | HttpResponseRedirect:
        """Check if time limit exceeded."""
        if not attempt.started_at:
            return True
            
        def handle_timeout(start: datetime, end: datetime) -> HttpResponseRedirect:
            messages.warning(
                request,
                'Quiz time limit exceeded. Your answers have been automatically submitted.'
            )
            self.complete_attempt(attempt)
            return redirect('quiz:quiz_results', quiz_id=attempt.quiz_id)
        
        time_limit = timedelta(minutes=self.get_time_limit())
        end_time = attempt.started_at + time_limit
        
        result = time_window(
            attempt.started_at,
            end_time,
            lambda s, e: True
        )
        
        return result if result else handle_timeout(
            attempt.started_at,
            end_time
        )
    
    def complete_attempt(self, attempt: QuizAttempt) -> None:
        """Complete quiz attempt."""
        if not attempt.completed_at:
            attempt.completed_at = timezone.now()
            attempt.time_taken = (
                attempt.completed_at - attempt.started_at
            ).total_seconds()
            attempt.save()
            
            # Invalidate cache
            cache_key = f'attempt_{attempt.user.id}_{attempt.quiz_id}'
            cache.delete(cache_key)
            completed_key = f'completed_{attempt.user.id}_{attempt.quiz_id}'
            cache.delete(completed_key)
            
            logger.info(f'Completed attempt {attempt.id}')
    
    def handle_quiz_error(
        self,
        request: HttpRequest,
        message: str,
        redirect_url: str = 'quiz:quiz_list',
        **kwargs
    ) -> HttpResponseRedirect:
        """Handle quiz error with redirect."""
        messages.error(request, message)
        return redirect(redirect_url, **kwargs)
