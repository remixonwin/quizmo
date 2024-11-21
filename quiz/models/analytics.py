"""
Analytics models with advanced functional programming patterns.
"""
from typing import Dict, List, Optional, Any, TypeVar, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Avg, Count, Q, F, Sum, Window
from django.db.models.functions import TruncDate, ExtractHour
from django.utils import timezone
from django.utils.functional import cached_property
from ..utils.functional import (
    immutable, memoize, pipe, compose,
    to_dict, safe_get, filter_none,
    group_by, map_values, curry,
    maybe, either
)
from .base import TimestampedModel, CachedModel
import logging
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)
User = get_user_model()
T = TypeVar('T')

@dataclass(frozen=True)
class UserPerformanceMetrics:
    """Immutable user performance metrics."""
    total_attempts: int = 0
    completed_attempts: int = 0
    total_time: float = 0.0
    average_score: float = 0.0
    pass_rate: float = 0.0
    accuracy_rate: float = 0.0
    improvement_rate: float = 0.0
    percentile: float = 0.0
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate."""
        return (self.completed_attempts / self.total_attempts * 100) if self.total_attempts else 0.0
    
    @property
    def average_time(self) -> float:
        """Calculate average time per attempt."""
        return self.total_time / self.completed_attempts if self.completed_attempts else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_attempts': self.total_attempts,
            'completed_attempts': self.completed_attempts,
            'completion_rate': self.completion_rate,
            'total_time': self.total_time,
            'average_time': self.average_time,
            'average_score': self.average_score,
            'pass_rate': self.pass_rate,
            'accuracy_rate': self.accuracy_rate,
            'improvement_rate': self.improvement_rate,
            'percentile': self.percentile
        }

@dataclass(frozen=True)
class TimeSeriesData:
    """Immutable time series data."""
    timestamps: List[datetime]
    values: List[float]
    trend: Optional[float] = None
    seasonality: Optional[Dict[str, float]] = None
    
    @property
    def length(self) -> int:
        return len(self.timestamps)
    
    @property
    def average(self) -> float:
        return sum(self.values) / self.length if self.length else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamps': [t.isoformat() for t in self.timestamps],
            'values': self.values,
            'trend': self.trend,
            'seasonality': self.seasonality,
            'average': self.average
        }

class UserPerformance(TimestampedModel, CachedModel):
    """User performance tracking with functional patterns."""
    
    user = models.ForeignKey(
        User,
        related_name='quiz_performance',
        on_delete=models.CASCADE
    )
    quiz = models.ForeignKey(
        'Quiz',
        related_name='user_performance',
        on_delete=models.CASCADE
    )
    last_attempt_at = models.DateTimeField(null=True)
    attempts_count = models.IntegerField(default=0)
    completed_count = models.IntegerField(default=0)
    total_time = models.FloatField(default=0.0)
    best_score = models.FloatField(null=True)
    average_score = models.FloatField(null=True)
    pass_count = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    total_answers = models.IntegerField(default=0)
    percentile_rank = models.FloatField(null=True)
    improvement_rate = models.FloatField(null=True)
    
    class Meta:
        unique_together = ['user', 'quiz']
        indexes = [
            models.Index(fields=['user', 'quiz', 'average_score']),
            models.Index(fields=['quiz', 'percentile_rank'])
        ]
    
    def __str__(self) -> str:
        return f"{self.user.username}'s performance in {self.quiz.title}"
    
    @memoize
    def get_metrics(self) -> UserPerformanceMetrics:
        """Get user performance metrics with caching."""
        return UserPerformanceMetrics(
            total_attempts=self.attempts_count,
            completed_attempts=self.completed_count,
            total_time=self.total_time,
            average_score=self.average_score or 0.0,
            pass_rate=(self.pass_count / self.completed_count * 100) 
                if self.completed_count else 0.0,
            accuracy_rate=(self.correct_answers / self.total_answers * 100)
                if self.total_answers else 0.0,
            improvement_rate=self.improvement_rate or 0.0,
            percentile=self.percentile_rank or 0.0
        )
    
    @memoize
    def get_score_history(self) -> TimeSeriesData:
        """Get score history with trend analysis."""
        attempts = (
            self.quiz.attempts
            .filter(user=self.user, completed_at__isnull=False)
            .order_by('completed_at')
            .values('completed_at', 'score')
        )
        
        if not attempts:
            return TimeSeriesData([], [])
        
        timestamps = [a['completed_at'] for a in attempts]
        scores = [a['score'] or 0.0 for a in attempts]
        
        # Calculate trend using linear regression
        x = np.arange(len(scores))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, scores)
        trend = slope  # Positive slope indicates improvement
        
        # Calculate seasonality by hour of day
        hours = [t.hour for t in timestamps]
        hour_scores = group_by(
            list(zip(hours, scores)),
            key=lambda x: x[0]
        )
        seasonality = {
            str(hour): sum(s for _, s in scores) / len(scores)
            for hour, scores in hour_scores.items()
        }
        
        return TimeSeriesData(
            timestamps=timestamps,
            values=scores,
            trend=trend,
            seasonality=seasonality
        )
    
    def update_from_attempt(self, attempt: 'QuizAttempt') -> None:
        """Update performance metrics from a new attempt."""
        if not attempt.is_completed:
            return
        
        self.attempts_count += 1
        self.completed_count += 1
        self.last_attempt_at = attempt.completed_at
        
        if attempt.time_taken:
            self.total_time += attempt.time_taken.total_seconds()
        
        # Update scores
        score = attempt.score or 0.0
        if self.best_score is None or score > self.best_score:
            self.best_score = score
        
        # Update average score
        if self.average_score is None:
            self.average_score = score
        else:
            self.average_score = (
                (self.average_score * (self.completed_count - 1) + score) /
                self.completed_count
            )
        
        # Update pass count
        if attempt.has_passed:
            self.pass_count += 1
        
        # Update answer stats
        answers = attempt.get_answers()
        correct = sum(1 for a in answers if a.is_correct)
        total = len(answers)
        self.correct_answers += correct
        self.total_answers += total
        
        # Calculate improvement rate
        previous_attempts = (
            self.quiz.attempts
            .filter(
                user=self.user,
                completed_at__lt=attempt.completed_at
            )
            .order_by('-completed_at')
            [:5]  # Look at last 5 attempts
        )
        
        if previous_attempts:
            prev_scores = [a.score or 0.0 for a in previous_attempts]
            avg_prev_score = sum(prev_scores) / len(prev_scores)
            self.improvement_rate = (
                (score - avg_prev_score) / avg_prev_score * 100
            ) if avg_prev_score else 0.0
        
        self.save()
        self._update_percentile()
    
    def _update_percentile(self) -> None:
        """Update percentile rank."""
        if self.average_score is None:
            return
        
        # Get all scores for this quiz
        scores = (
            UserPerformance.objects
            .filter(quiz=self.quiz)
            .exclude(average_score__isnull=True)
            .values_list('average_score', flat=True)
        )
        
        if not scores:
            self.percentile_rank = 100.0
            return
        
        # Calculate percentile rank
        scores = sorted(scores)
        rank = next(
            (i for i, s in enumerate(scores) if s >= self.average_score),
            len(scores)
        )
        self.percentile_rank = (rank / len(scores)) * 100
        self.save(update_fields=['percentile_rank'])
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save performance and invalidate caches."""
        super().save(*args, **kwargs)
        
        # Clear cached data
        self.get_metrics.cache_clear()
        self.get_score_history.cache_clear()
        
        # Clear related caches
        cache.delete_many([
            f'user_performance_{self.user_id}_{self.quiz_id}',
            f'quiz_leaderboard_{self.quiz_id}'
        ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert performance to dictionary."""
        return {
            'user': self.user.username,
            'quiz': self.quiz.title,
            'metrics': self.get_metrics().to_dict(),
            'score_history': self.get_score_history().to_dict(),
            'last_attempt': self.last_attempt_at.isoformat() if self.last_attempt_at else None
        }
