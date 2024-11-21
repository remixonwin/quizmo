"""
Quiz model with functional programming patterns.
"""
from typing import Dict, List, Optional, Any, Tuple
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.cache import cache
from ..utils.functional import (
    immutable, memoize, pipe, compose,
    to_dict, safe_get, filter_none,
    group_by, map_values
)
from .base import TimestampedModel, OrderedMixin, CachedMixin
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@immutable
class QuizStats:
    """Immutable quiz statistics."""
    
    def __init__(
        self,
        total_attempts: int,
        average_score: float,
        pass_rate: float,
        average_time: float,
        completion_rate: float
    ):
        self._total_attempts = total_attempts
        self._average_score = average_score
        self._pass_rate = pass_rate
        self._average_time = average_time
        self._completion_rate = completion_rate
    
    @property
    def total_attempts(self) -> int:
        return self._total_attempts
    
    @property
    def average_score(self) -> float:
        return self._average_score
    
    @property
    def pass_rate(self) -> float:
        return self._pass_rate
    
    @property
    def average_time(self) -> float:
        return self._average_time
    
    @property
    def completion_rate(self) -> float:
        return self._completion_rate
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_attempts': self.total_attempts,
            'average_score': self.average_score,
            'pass_rate': self.pass_rate,
            'average_time': self.average_time,
            'completion_rate': self.completion_rate
        }

class Quiz(TimestampedModel, OrderedMixin, CachedMixin):
    """Quiz model with functional programming patterns."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pass_mark = models.FloatField(default=70.0)
    time_limit = models.IntegerField(
        default=30,
        help_text='Time limit in minutes'
    )
    is_active = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=True)
    show_answers = models.BooleanField(
        default=False,
        help_text='Show correct answers after completion'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.title
    
    @memoize
    def get_questions(self) -> models.QuerySet:
        """Get quiz questions with caching."""
        return (
            self.questions
            .select_related()
            .prefetch_related('choices')
            .filter(is_active=True)
            .order_by('order')
        )
    
    @memoize
    def get_stats(self) -> QuizStats:
        """Get quiz statistics with caching."""
        attempts = self.attempts.all()
        total_attempts = attempts.count()
        
        if not total_attempts:
            return QuizStats(0, 0.0, 0.0, 0.0, 0.0)
        
        completed_attempts = [a for a in attempts if a.is_completed]
        completed_count = len(completed_attempts)
        
        if not completed_count:
            return QuizStats(
                total_attempts=total_attempts,
                average_score=0.0,
                pass_rate=0.0,
                average_time=0.0,
                completion_rate=0.0
            )
        
        scores = [a.score for a in completed_attempts if a.score is not None]
        times = [a.time_taken for a in completed_attempts if a.time_taken is not None]
        passed = sum(1 for a in completed_attempts if a.has_passed)
        
        return QuizStats(
            total_attempts=total_attempts,
            average_score=sum(scores) / len(scores) if scores else 0.0,
            pass_rate=(passed / completed_count) * 100 if completed_count else 0.0,
            average_time=sum(t.total_seconds() for t in times) / len(times) if times else 0.0,
            completion_rate=(completed_count / total_attempts) * 100
        )
    
    @memoize
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get quiz leaderboard with caching."""
        return list(
            self.attempts
            .filter(completed_at__isnull=False)
            .select_related('user')
            .order_by('-score', 'time_taken')
            .values('user__username', 'score', 'time_taken')
            [:limit]
        )
    
    def start_attempt(self, user: User) -> 'QuizAttempt':
        """Start a new quiz attempt."""
        from .attempt import QuizAttempt
        
        # Check for active attempts
        active_attempt = (
            QuizAttempt.objects
            .filter(
                quiz=self,
                user=user,
                completed_at__isnull=True
            )
            .first()
        )
        
        if active_attempt:
            raise ValidationError('User has an active attempt')
        
        attempt = QuizAttempt.objects.create(
            quiz=self,
            user=user
        )
        attempt.start()
        
        logger.info(f'Started attempt {attempt.id} for quiz {self.id}')
        return attempt
    
    def validate_answer(self, question_id: int, choice_id: int) -> Tuple[bool, str]:
        """Validate a question answer."""
        question = (
            self.questions
            .filter(id=question_id)
            .prefetch_related('choices')
            .first()
        )
        
        if not question:
            return False, 'Invalid question'
            
        choice = question.choices.filter(id=choice_id).first()
        
        if not choice:
            return False, 'Invalid choice'
            
        return True, ''
    
    def calculate_score(self, attempt: 'QuizAttempt') -> Dict[str, Any]:
        """Calculate score for an attempt."""
        if not attempt.is_completed:
            return {
                'score': 0.0,
                'correct_answers': 0,
                'total_questions': 0,
                'passed': False
            }
        
        answers = attempt.get_answers()
        total_questions = self.get_questions().count()
        correct_answers = sum(1 for a in answers if a.is_correct)
        
        score = (correct_answers / total_questions * 100) if total_questions else 0
        
        return {
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'passed': score >= self.pass_mark
        }
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save quiz and invalidate caches."""
        super().save(*args, **kwargs)
        
        # Clear cached data
        self.get_questions.cache_clear()
        self.get_stats.cache_clear()
        self.get_leaderboard.cache_clear()
        
        # Clear related caches
        cache.delete_many([
            f'quiz_stats_{self.id}',
            f'quiz_leaderboard_{self.id}'
        ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quiz to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'pass_mark': self.pass_mark,
            'time_limit': self.time_limit,
            'is_active': self.is_active,
            'randomize_questions': self.randomize_questions,
            'show_answers': self.show_answers,
            'stats': self.get_stats().to_dict(),
            'questions_count': self.get_questions().count()
        }
