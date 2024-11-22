"""
Quiz model with functional programming patterns.
"""
from typing import Dict, Any, List
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from ..utils.model_utils import BaseModel, TimestampedModel, OrderedMixin, CachedMixin
from ..utils.functional import (
    immutable, memoize, pipe, compose,
    to_dict, safe_get, filter_none,
    group_by, map_values
)
import logging
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils.text import slugify
import uuid
from .question import Question

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
    """Quiz model."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    time_limit = models.IntegerField(default=30, help_text='Time limit in minutes')
    pass_mark = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    success_text = models.TextField(blank=True, help_text='Displayed when user passes the quiz')
    fail_text = models.TextField(blank=True, help_text='Displayed when user fails the quiz')
    max_attempts = models.IntegerField(default=0, help_text='0 = unlimited attempts')
    random_order = models.BooleanField(default=False)
    answers_at_end = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    image = models.ImageField(upload_to='quiz_images/', null=True, blank=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        """Save quiz and generate slug if needed."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Keep trying with incremented counter until we find a unique slug
            while Quiz.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError('Start date must be before end date')
            
    @property
    def is_ended(self):
        if self.end_date:
            return timezone.now() >= self.end_date
        return False
    
    @property
    def status(self):
        if not self.is_active:
            return 'inactive'
        if self.is_ended:
            return 'ended'
        return 'active'

    @property
    def question_count(self):
        return self.questions.count()
    
    @property
    def total_attempts(self):
        return self.attempts.count()
    
    def get_user_attempts(self, user):
        return self.attempts.filter(user=user).count()
    
    def get_best_score(self, user):
        best_attempt = self.attempts.filter(user=user).order_by('-score').first()
        return best_attempt.score if best_attempt else None

class QuizAttempt(TimestampedModel):
    """Model to track quiz attempts."""
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username}'s attempt at {self.quiz.title}"
    
    @property
    def is_completed(self):
        return bool(self.completed_at)
    
    @property
    def time_taken(self):
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class QuizAnswer(TimestampedModel):
    """Model to store user's answers to quiz questions."""
    
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey('quiz.Choice', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('attempt', 'question')
        ordering = ['question__order', 'created_at']

    def __str__(self):
        return f"{self.attempt.user.username}'s answer to {self.question.text[:50]}"
