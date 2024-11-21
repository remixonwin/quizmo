"""
Question and Choice models with advanced functional programming patterns.
"""
from typing import Dict, List, Optional, Any, TypeVar, Union, Callable
from dataclasses import dataclass, field
from django.db import models
from django.db.models import Avg, Count
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db.models import Q, F
from django.utils.functional import cached_property
from ..utils.functional import (
    immutable, memoize, pipe, compose,
    to_dict, safe_get, filter_none,
    group_by, map_values, curry,
    maybe, Either, Maybe, fmap, bind
)
from .base import TimestampedModel, OrderedMixin, CachedMixin
import logging
from decimal import Decimal
from typing_extensions import Protocol
import numpy as np
from statistics import mean, median

logger = logging.getLogger(__name__)
T = TypeVar('T')
S = TypeVar('S')

# Type protocols
class HasScore(Protocol):
    score: Optional[float]

class HasTimeTaken(Protocol):
    time_taken: Optional[float]

# Pure functions for calculations
def calculate_success_rate(correct: int, total: int) -> float:
    """Pure function to calculate success rate."""
    return (correct / total * 100) if total else 0.0

def calculate_error_rate(incorrect: int, total: int) -> float:
    """Pure function to calculate error rate."""
    return (incorrect / total * 100) if total else 0.0

from .metrics import (
    AnswerMetrics,
    TimeDistribution,
    calculate_discrimination,
    calculate_point_biserial
)

@dataclass(frozen=True)
class QuestionMetrics:
    """Immutable question metrics."""
    difficulty_score: float = 0.0
    discrimination_index: float = 0.0
    average_time: float = 0.0
    point_biserial: float = 0.0

@dataclass(frozen=True)
class QuestionStats:
    """Immutable question statistics with advanced metrics."""
    answers: AnswerMetrics
    metrics: QuestionMetrics
    attempts_distribution: Dict[str, int] = field(default_factory=dict)
    time_distribution: TimeDistribution = field(default_factory=TimeDistribution)
    
    @staticmethod
    def create(
        answers: List['UserAnswer'],
        attempts: List['QuizAttempt']
    ) -> 'QuestionStats':
        """Factory method to create QuestionStats."""
        if not answers:
            return QuestionStats(
                AnswerMetrics(),
                QuestionMetrics(),
                {},
                TimeDistribution()
            )
        
        # Calculate answer metrics using pure functions
        total = len(answers)
        correct = sum(1 for a in answers if a.is_correct)
        
        answer_metrics = AnswerMetrics(
            total=total,
            correct=correct,
            incorrect=total - correct
        )
        
        # Calculate discrimination index using pure function
        if len(attempts) >= 2:
            sorted_attempts = sorted(attempts, key=lambda a: a.score or 0)
            n = max(1, int(len(sorted_attempts) * 0.27))
            discrimination = calculate_discrimination(
                answers,
                sorted_attempts[-n:],
                sorted_attempts[:n]
            )
        else:
            discrimination = 0.0
        
        # Calculate time metrics using pure functions
        times = [
            a.attempt.time_taken.total_seconds()
            for a in answers
            if a.attempt.time_taken
        ]
        
        # Calculate point-biserial using pure function
        correct_scores = [
            a.attempt.score
            for a in answers
            if a.is_correct and a.attempt.score
        ]
        incorrect_scores = [
            a.attempt.score
            for a in answers
            if not a.is_correct and a.attempt.score
        ]
        
        point_biserial = calculate_point_biserial(
            correct_scores,
            incorrect_scores,
            total
        )
        
        # Create metrics using pure data
        question_metrics = QuestionMetrics(
            difficulty_score=calculate_success_rate(correct, total),
            discrimination_index=discrimination,
            average_time=mean(times) if times else 0,
            point_biserial=point_biserial
        )
        
        # Calculate distributions using pure functions
        attempts_dist = group_by(
            answers,
            key=lambda a: a.attempt.user.username
        )
        
        time_dist = TimeDistribution.from_times(times)
        
        return QuestionStats(
            answers=answer_metrics,
            metrics=question_metrics,
            attempts_distribution=attempts_dist,
            time_distribution=time_dist
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'answers': {
                'total': self.answers.total,
                'correct': self.answers.correct,
                'incorrect': self.answers.incorrect,
                'success_rate': self.answers.success_rate,
                'error_rate': self.answers.error_rate
            },
            'metrics': {
                'difficulty_score': self.metrics.difficulty_score,
                'discrimination_index': self.metrics.discrimination_index,
                'average_time': self.metrics.average_time,
                'point_biserial': self.metrics.point_biserial
            },
            'distributions': {
                'attempts': self.attempts_distribution,
                'time': {
                    'min': self.time_distribution.min_time,
                    'max': self.time_distribution.max_time,
                    'avg': self.time_distribution.avg_time,
                    'median': self.time_distribution.median_time
                }
            }
        }

class Question(TimestampedModel, OrderedMixin, CachedMixin):
    """Question model with advanced functional patterns."""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]
    
    quiz = models.ForeignKey(
        'Quiz',
        related_name='questions',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    explanation = models.TextField(
        blank=True,
        help_text='Explanation shown after answering'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0
    )
    is_active = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)
    image = models.ImageField(
        upload_to='question_images/',
        null=True,
        blank=True,
        help_text='Image to display with the question'
    )
    
    class Meta:
        ordering = ['quiz', 'order']
        unique_together = ['quiz', 'order']
    
    def __str__(self) -> str:
        return f"{self.quiz.title} - Q{self.order}"
    
    @cached_property
    def choices_count(self) -> int:
        """Get number of choices."""
        return self.choices.count()
    
    @memoize
    def get_choices(self) -> models.QuerySet:
        """Get question choices with caching."""
        return (
            self.choices
            .select_related()
            .filter(is_active=True)
            .order_by('order')
            .annotate(
                selection_count=Count('answers'),
                selection_rate=100.0 * F('selection_count') /
                    Count('question__answers', filter=Q(question=F('question')))
            )
        )
    
    @memoize
    def get_stats(self) -> QuestionStats:
        """Get question statistics with caching."""
        answers = list(
            self.answers
            .select_related('choice', 'attempt', 'attempt__user')
            .all()
        )
        attempts = list(
            self.quiz.attempts
            .filter(completed_at__isnull=False)
            .select_related('user')
            .all()
        )
        
        return QuestionStats.create(answers, attempts)
    
    def validate_choice(self, choice_id: int) -> Either['Choice']:
        """
        Validate choice with Either monad.
        
        Args:
            choice_id: Choice ID to validate
            
        Returns:
            Either monad containing Choice or error message
        """
        try:
            choice = self.choices.get(id=choice_id)
            return Either(right=choice)
        except Choice.DoesNotExist:
            return Either(left='Invalid choice')
    
    def get_correct_choice(self) -> Maybe['Choice']:
        """
        Get correct choice with Maybe monad.
        
        Args:
            None
            
        Returns:
            Maybe monad containing correct Choice or None
        """
        return maybe(
            self.choices.filter(is_correct=True).first()
        )
    
    @curry
    def apply_points(
        self,
        is_correct: bool,
        time_taken: float
    ) -> Decimal:
        """Calculate points with time bonus."""
        base_points = self.points
        if not is_correct:
            return Decimal('0')
        
        # Time bonus: up to 20% extra points for fast answers
        time_limit = self.quiz.time_limit * 60  # convert to seconds
        if time_taken <= time_limit / 2:
            bonus = Decimal('0.2')
        elif time_taken <= time_limit * 0.75:
            bonus = Decimal('0.1')
        else:
            bonus = Decimal('0')
        
        return base_points * (1 + bonus)
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save question and invalidate caches."""
        super().save(*args, **kwargs)
        
        # Clear cached data
        self.get_choices.cache_clear()
        self.get_stats.cache_clear()
        
        # Clear related caches
        cache.delete_many([
            f'question_stats_{self.id}',
            f'quiz_questions_{self.quiz_id}'
        ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary."""
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'text': self.text,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'points': float(self.points),
            'is_active': self.is_active,
            'order': self.order,
            'tags': self.tags,
            'stats': self.get_stats().to_dict(),
            'choices': [c.to_dict() for c in self.get_choices()]
        }

class Choice(TimestampedModel, OrderedMixin, CachedMixin):
    """Choice model with advanced functional patterns."""
    
    question = models.ForeignKey(
        'Question',
        related_name='choices',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(
        blank=True,
        help_text='Explanation shown when this choice is selected'
    )
    is_active = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['question', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'order'],
                name='unique_choice_order_per_question'
            )
        ]

    def __str__(self) -> str:
        return f"{self.question} - Choice {self.order}"
    
    @cached_property
    def selection_count(self) -> int:
        """Get number of times this choice was selected."""
        return self.answers.count()
    
    @memoize
    def get_stats(self) -> Dict[str, Any]:
        """Get choice statistics with caching."""
        total_answers = self.question.answers.count()
        
        if not total_answers:
            return {
                'selections': 0,
                'selection_rate': 0.0,
                'correct_selections': 0,
                'incorrect_selections': 0
            }
        
        answers = list(self.answers.all())
        selections = len(answers)
        
        # Use pure functions for calculations
        return {
            'selections': selections,
            'selection_rate': calculate_success_rate(selections, total_answers),
            'correct_selections': sum(1 for a in answers if a.is_correct),
            'incorrect_selections': sum(1 for a in answers if not a.is_correct)
        }
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save choice and invalidate caches."""
        # Ensure only one correct choice per question using functional patterns
        if self.is_correct:
            pipe(
                self.question.choices.exclude(id=self.id),
                lambda qs: qs.update(is_correct=False)
            )
        
        super().save(*args, **kwargs)
        
        # Clear cached data using functional patterns
        pipe(
            [
                lambda: self.get_stats.cache_clear() if hasattr(self, 'get_stats') else None,
                lambda: cache.delete_many([
                    f'question_choices_{self.question_id}',
                    f'question_stats_{self.question_id}'
                ])
            ],
            lambda fs: [f() for f in fs]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert choice to dictionary."""
        return pipe(
            {
                'id': self.id,
                'question_id': self.question_id,
                'text': self.text,
                'is_correct': self.is_correct,
                'explanation': self.explanation,
                'is_active': self.is_active,
                'order': self.order,
                'tags': self.tags
            },
            lambda d: {**d, 'stats': self.get_stats()}
        )
