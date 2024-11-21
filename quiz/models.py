"""
Quiz models with functional programming patterns.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()

class Quiz(models.Model):
    """Quiz model."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    pass_mark = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ]
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'quizzes'
        ordering = ['-created_at']

class Question(models.Model):
    """Question model."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    explanation = models.TextField(blank=True)
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"
    
    class Meta:
        ordering = ['order', 'id']

class Choice(models.Model):
    """Choice model."""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = [('question', 'order')]

class QuizAttempt(models.Model):
    """Quiz attempt model."""
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    time_taken = models.FloatField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
    
    class Meta:
        ordering = ['-started_at']

class UserAnswer(models.Model):
    """User answer model."""
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name='user_answers'
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.PROTECT,
        related_name='user_answers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.text[:50]}"
    
    class Meta:
        ordering = ['created_at']
