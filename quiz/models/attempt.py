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
        self._score = score
        self._correct_answers = correct_answers
        self._total_questions = total_questions
        self._time_taken = time_taken
        self._passed = passed
    
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
    def is_in_progress(self) -> bool:
        """Check if attempt is in progress."""
        return bool(self.started_at and not self.completed_at)
    
    @property
    def has_passed(self) -> bool:
        """Check if attempt passed."""
        return bool(
            self.score is not None and
            self.score >= self.quiz.pass_mark
        )
    
    @memoize
    def get_answers(self) -> models.QuerySet:
        """Get attempt answers with caching."""
        return self.answers.select_related('question', 'choice')
    
    @memoize
    def get_result(self) -> AttemptResult:
        """Get attempt result."""
        if not self.is_completed:
            return None
            
        answers = self.get_answers()
        total_questions = self.quiz.questions.count()
        correct_answers = sum(
            1 for a in answers
            if a.choice and a.choice.is_correct
        )
        
        score = (correct_answers / total_questions * 100) if total_questions else 0
        
        return AttemptResult(
            score=score,
            correct_answers=correct_answers,
            total_questions=total_questions,
            time_taken=self.time_taken or 0,
            passed=score >= self.quiz.pass_mark
        )
    
    def start(self) -> None:
        """Start quiz attempt."""
        if self.started_at:
            raise ValidationError('Attempt already started')
            
        self.started_at = timezone.now()
        self.save()
        logger.info(f'Started attempt {self.id}')
    
    def complete(self) -> None:
        """Complete quiz attempt."""
        if self.completed_at:
            raise ValidationError('Attempt already completed')
            
        if not self.started_at:
            raise ValidationError('Attempt not started')
            
        now = timezone.now()
        self.completed_at = now
        self.time_taken = (now - self.started_at).total_seconds()
        
        # Calculate result
        result = self.get_result()
        if result:
            self.score = result.score
            
        self.save()
        logger.info(f'Completed attempt {self.id} with score {self.score}')
    
    def add_answer(self, question_id: int, choice_id: int) -> 'UserAnswer':
        """Add answer to attempt."""
        if self.is_completed:
            raise ValidationError('Cannot add answer to completed attempt')
            
        if not self.is_in_progress:
            raise ValidationError('Attempt not in progress')
            
        from .question import Question, Choice
        
        # Validate question and choice
        question = Question.objects.filter(
            quiz=self.quiz,
            id=question_id
        ).first()
        
        if not question:
            raise ValidationError('Invalid question')
            
        choice = Choice.objects.filter(
            question=question,
            id=choice_id
        ).first()
        
        if not choice:
            raise ValidationError('Invalid choice')
            
        # Create answer
        answer = UserAnswer.objects.create(
            attempt=self,
            question=question,
            choice=choice
        )
        
        logger.info(f'Added answer {answer.id} to attempt {self.id}')
        return answer
    
    def save(self, *args, **kwargs):
        """Save attempt and clear caches."""
        # Clear cached answers
        if hasattr(self.get_answers, 'cache_clear'):
            self.get_answers.cache_clear()
        
        # Clear cached result
        if hasattr(self.get_result, 'cache_clear'):
            self.get_result.cache_clear()
        
        super().save(*args, **kwargs)

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
            'question': self.question.text,
            'choice': self.choice.text if self.choice else None,
            'is_correct': self.is_correct
        }
