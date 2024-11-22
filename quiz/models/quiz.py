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

class Quiz(models.Model):
    """Quiz model."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True, blank=True)
    passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=60.00,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ]
    )
    
    def __str__(self):
        return self.title
        
    def clean(self):
        if self.end_date and self.end_date < timezone.now():
            raise ValidationError('End date cannot be in the past.')
            
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    @property
    def is_ended(self):
        return self.end_date and self.end_date < timezone.now()
        
    @property
    def status(self):
        if not self.is_active:
            return 'inactive'
        if not self.is_published:
            return 'draft'
        if self.is_ended:
            return 'ended'
        return 'active'
