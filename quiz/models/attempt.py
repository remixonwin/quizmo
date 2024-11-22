"""
Quiz attempt and user answer models with functional patterns.
"""
from typing import Dict, List, Optional, Any
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.contrib.auth import get_user_model
from ..utils.functional import (
    immutable, memoize, pipe, compose,
    to_dict, safe_get, filter_none,
    group_by, map_values, curry,
    maybe, Either, Maybe, fmap, bind
)
from .base import TimestampedModel, CachedMixin
from .quiz import Quiz
from .question import Question, Choice
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@immutable
class AttemptResult:
    """Immutable attempt result."""
    
    def __init__(
        self,
        score: float,
        correct_answers: int,
        total_questions: int,
        time_taken: float,
        passed: bool
    ):
        # Use object.__setattr__ to bypass immutability during initialization
        object.__setattr__(self, '_score', score)
        object.__setattr__(self, '_correct_answers', correct_answers)
        object.__setattr__(self, '_total_questions', total_questions)
        object.__setattr__(self, '_time_taken', time_taken)
        object.__setattr__(self, '_passed', passed)
    
    @property
    def score(self) -> float:
        return self._score
    
    @property
    def correct_answers(self) -> int:
        return self._correct_answers
    
    @property
    def total_questions(self) -> int:
        return self._total_questions
    
    @property
    def time_taken(self) -> float:
        return self._time_taken
    
    @property
    def passed(self) -> bool:
        return self._passed
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'correct_answers': self.correct_answers,
            'total_questions': self.total_questions,
            'time_taken': self.time_taken,
            'passed': self.passed
        }

class QuizAttempt(TimestampedModel, CachedMixin):
    """Quiz attempt model with functional patterns."""
    
    quiz = models.ForeignKey(
        Quiz,
        related_name='attempts',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name='quiz_attempts',
        on_delete=models.CASCADE
    )
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    score = models.FloatField(null=True)
    time_taken = models.FloatField(null=True)  # seconds
    metadata = models.JSONField(null=True, blank=True, default=dict)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['quiz', 'user', 'started_at']
    
    def __str__(self) -> str:
        return f'{self.user.username} - {self.quiz.title}'
    
    @property
    def is_completed(self) -> bool:
        """Check if attempt is completed."""
        return bool(self.completed_at)
    
    @property
    def time_remaining(self) -> int:
        """Get remaining time in seconds."""
        if not self.started_at or self.is_completed:
            return 0
        
        elapsed = (timezone.now() - self.started_at).total_seconds()
        remaining = (self.quiz.time_limit * 60) - elapsed
        
        return max(0, int(remaining))
    
    def start(self) -> None:
        """Start the quiz attempt."""
        if self.started_at:
            raise ValidationError('Attempt already started')
            
        self.started_at = timezone.now()
        self.save()
        
        logger.info(f'Started attempt {self.id} for quiz {self.quiz.id}')
    
    def complete(self) -> None:
        """Complete the quiz attempt."""
        if self.completed_at:
            raise ValidationError('Attempt already completed')
            
        if not self.started_at:
            raise ValidationError('Attempt not started')
            
        self.completed_at = timezone.now()
        self.time_taken = (self.completed_at - self.started_at).total_seconds()
        
        # Calculate score
        total_questions = self.quiz.total_questions
        correct_answers = self.answers.filter(choice__is_correct=True).count()
        self.score = (correct_answers / total_questions) * 100
        
        self.save()
        
        logger.info(f'Completed attempt {self.id} for quiz {self.quiz.id}')
    
    @property
    def has_passed(self) -> bool:
        """Check if attempt has passed."""
        if not self.is_completed or self.score is None:
            return False
        return self.score >= self.quiz.passing_score
    
    def get_result(self) -> AttemptResult:
        """Get attempt result."""
        if not self.is_completed:
            raise ValidationError('Attempt not completed')
            
        return AttemptResult(
            score=self.score,
            correct_answers=self.answers.filter(choice__is_correct=True).count(),
            total_questions=self.quiz.total_questions,
            time_taken=self.time_taken,
            passed=self.has_passed
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert attempt to dictionary."""
        return {
            'id': self.id,
            'quiz': self.quiz.title,
            'user': self.user.username,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'score': self.score,
            'time_taken': self.time_taken,
            'passed': self.has_passed,
            'answers_count': self.answers.count()
        }


class UserAnswer(TimestampedModel):
    """User answer model."""
    
    attempt = models.ForeignKey(
        QuizAttempt,
        related_name='answers',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        'Question',
        related_name='answers',
        on_delete=models.CASCADE
    )
    choice = models.ForeignKey(
        'Choice',
        related_name='answers',
        on_delete=models.CASCADE,
        null=True
    )
    
    class Meta:
        ordering = ['created_at']
        unique_together = ['attempt', 'question']
    
    def __str__(self) -> str:
        return f'{self.attempt} - {self.question}'
    
    @property
    def is_correct(self) -> bool:
        """Check if answer is correct."""
        return bool(self.choice and self.choice.is_correct)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert answer to dictionary."""
        return {
            'id': self.id,
            'attempt': self.attempt.id,
            'question': self.question.text,
            'choice': self.choice.text if self.choice else None,
            'is_correct': self.is_correct
        }
