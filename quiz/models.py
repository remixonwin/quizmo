from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Index
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Quiz(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='quiz_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title', 'created_at']),
            models.Index(fields=['is_active', 'created_at']),
        ]
        verbose_name_plural = "Quizzes"
    
    def __str__(self):
        return self.title
    
    def get_questions(self):
        return self.questions.all()

    def calculate_score(self):
        """Calculate quiz score with caching"""
        cache_key = f'quiz_score_{self.id}'
        score_data = cache.get(cache_key)
        
        if score_data is None:
            total_questions = self.questions.count()
            correct_answers = sum(1 for q in self.questions.all() if q.choices.filter(is_correct=True).exists())
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            passed = correct_answers >= 32  # Need 32 out of 40 to pass
            
            score_data = {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'score': score,
                'passed': passed,
                'required_to_pass': 32
            }
            
            cache.set(cache_key, score_data, 3600)  # Cache for 1 hour
        
        return score_data

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    explanation = models.TextField(blank=True)
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['quiz', 'order']),
        ]
    
    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"
    
    def get_choices(self):
        return self.choices.all()

    def get_correct_choice(self):
        """Get correct choice with caching"""
        cache_key = f'question_correct_choice_{self.id}'
        correct_choice = cache.get(cache_key)
        
        if correct_choice is None:
            correct_choice = self.choices.filter(is_correct=True).first()
            if correct_choice:
                cache.set(cache_key, correct_choice, 3600)  # Cache for 1 hour
        
        return correct_choice

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['question', 'is_correct']),
        ]
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.text[:30]}"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, related_name='quiz_attempts', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='attempts', on_delete=models.CASCADE)
    score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(default=timezone.now)
    time_taken = models.DurationField()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'quiz', 'created_at']),
            models.Index(fields=['quiz', 'score']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"

# Signal handlers for cache invalidation
@receiver([post_save, post_delete], sender=Quiz)
def invalidate_quiz_cache(sender, instance, **kwargs):
    """Invalidate quiz-related caches"""
    cache.delete(f'quiz_score_{instance.id}')
    cache.delete('quiz_list')

@receiver([post_save, post_delete], sender=Question)
def invalidate_question_cache(sender, instance, **kwargs):
    """Invalidate question-related caches"""
    cache.delete(f'quiz_score_{instance.quiz_id}')
    cache.delete(f'question_correct_choice_{instance.id}')

@receiver([post_save, post_delete], sender=Choice)
def invalidate_choice_cache(sender, instance, **kwargs):
    """Invalidate choice-related caches"""
    cache.delete(f'question_correct_choice_{instance.question_id}')
