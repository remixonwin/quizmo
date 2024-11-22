"""
Question bank model for managing shared questions.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .base import TimestampedModel, CachedMixin
from ..utils.functional import immutable, to_dict
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@immutable
class BankStats:
    """Immutable question bank statistics."""
    
    def __init__(
        self,
        total_questions: int,
        total_quizzes: int,
        average_difficulty: float,
        usage_count: int
    ):
        self._total_questions = total_questions
        self._total_quizzes = total_quizzes
        self._average_difficulty = average_difficulty
        self._usage_count = usage_count
    
    @property
    def total_questions(self) -> int:
        return self._total_questions
    
    @property
    def total_quizzes(self) -> int:
        return self._total_quizzes
    
    @property
    def average_difficulty(self) -> float:
        return self._average_difficulty
    
    @property
    def usage_count(self) -> int:
        return self._usage_count
    
    def to_dict(self) -> dict:
        """Convert stats to dictionary."""
        return {
            'total_questions': self.total_questions,
            'total_quizzes': self.total_quizzes,
            'average_difficulty': self.average_difficulty,
            'usage_count': self.usage_count
        }


class QuestionBank(TimestampedModel, CachedMixin):
    """Question bank model for shared questions."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='question_banks'
    )
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'is_active'])
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def get_questions(self):
        """Get bank questions with caching."""
        cache_key = f'bank_questions_{self.id}'
        questions = cache.get(cache_key)
        
        if questions is None:
            questions = list(self.questions.filter(is_active=True))
            cache.set(cache_key, questions, 300)  # Cache for 5 minutes
        
        return questions
    
    def get_stats(self) -> BankStats:
        """Get bank statistics with caching."""
        cache_key = f'bank_stats_{self.id}'
        stats = cache.get(cache_key)
        
        if stats is None:
            questions = self.get_questions()
            total_questions = len(questions)
            total_quizzes = self.quizzes.count()
            
            # Calculate average difficulty
            if total_questions > 0:
                difficulties = {
                    'easy': 1.0,
                    'medium': 2.0,
                    'hard': 3.0
                }
                total_difficulty = sum(
                    difficulties.get(q.difficulty, 2.0)
                    for q in questions
                )
                average_difficulty = total_difficulty / total_questions
            else:
                average_difficulty = 0.0
            
            # Count total usage across all quizzes
            usage_count = sum(
                q.answers.count()
                for q in questions
            )
            
            stats = BankStats(
                total_questions=total_questions,
                total_quizzes=total_quizzes,
                average_difficulty=average_difficulty,
                usage_count=usage_count
            )
            cache.set(cache_key, stats, 300)  # Cache for 5 minutes
        
        return stats
    
    def save(self, *args, **kwargs) -> None:
        """Save bank and invalidate caches."""
        super().save(*args, **kwargs)
        
        # Clear cached data
        cache.delete_many([
            f'bank_questions_{self.id}',
            f'bank_stats_{self.id}'
        ])
    
    def to_dict(self) -> dict:
        """Convert bank to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'owner': self.owner.username,
            'tags': self.tags,
            'stats': self.get_stats().to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
