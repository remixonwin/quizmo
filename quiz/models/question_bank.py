"""
Question bank model for managing question collections.
"""
from django.db import models
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from typing import List, Optional
import logging
from .base import CachedMixin
from django.db import transaction

logger = logging.getLogger(__name__)

CACHE_TTL = 3600  # 1 hour cache TTL

class QuestionBank(CachedMixin, models.Model):
    """Model for managing question collections."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'is_active']),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def get_questions(self, limit: Optional[int] = None) -> models.QuerySet:
        """Get bank questions with efficient caching."""
        cache_key = self.get_cache_key(f'bank_questions_{self.id}')
        questions = cache.get(cache_key)
        
        if questions is None:
            try:
                questions = (self.questions
                           .select_related('bank')
                           .prefetch_related('choices')
                           .filter(is_active=True)
                           .order_by('order'))
                
                if limit:
                    questions = questions[:limit]
                
                questions = list(questions)
                cache.set(cache_key, questions, CACHE_TTL)
                logger.debug(f'Successfully cached bank questions for bank {self.id}')
                
            except Exception as e:
                logger.error(f'Error fetching bank questions: {str(e)}')
                return []
        
        return questions
    
    def add_questions_to_quiz(self, quiz, count: int = 10) -> List[models.Model]:
        """Add questions from bank to quiz."""
        from .question import Question, Choice
        
        try:
            logger.info(f'Adding questions from bank {self.id} to quiz {quiz.id}')
            
            # Get active questions from bank
            bank_questions = self.get_questions(limit=count)
            
            if not bank_questions:
                logger.warning(f'No questions available in bank {self.id}')
                return []
            
            logger.info(f'Found {len(bank_questions)} questions in bank {self.id}')
            
            # Create quiz questions
            quiz_questions = []
            with transaction.atomic():
                for i, bank_question in enumerate(bank_questions):
                    logger.debug(f'Creating quiz question {i+1} from bank question {bank_question.id}')
                    
                    # Create question
                    quiz_question = Question.objects.create(
                        quiz=quiz,
                        text=bank_question.text,
                        explanation=bank_question.explanation,
                        image=bank_question.image,
                        order=i
                    )
                    
                    # Get bank choices
                    bank_choices = bank_question.get_choices()
                    if not bank_choices:
                        logger.error(f'No choices found for bank question {bank_question.id}')
                        raise ValueError(f'Bank question {bank_question.id} has no choices')
                    
                    # Create quiz choices
                    quiz_choices = []
                    for bank_choice in bank_choices:
                        quiz_choices.append(
                            Choice(
                                question=quiz_question,
                                text=bank_choice.text,
                                is_correct=bank_choice.is_correct,
                                explanation=bank_choice.explanation
                            )
                        )
                    
                    # Bulk create choices
                    Choice.objects.bulk_create(quiz_choices)
                    quiz_questions.append(quiz_question)
                    
                    logger.debug(f'Created quiz question {quiz_question.id} with {len(quiz_choices)} choices')
            
            logger.info(f'Successfully added {len(quiz_questions)} questions to quiz {quiz.id}')
            return quiz_questions
            
        except Exception as e:
            logger.error(f'Error adding bank questions to quiz: {str(e)}', exc_info=True)
            return []

class BankQuestion(CachedMixin, models.Model):
    """Model for bank questions."""
    bank = models.ForeignKey(QuestionBank, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    explanation = models.TextField(blank=True)
    image = models.ImageField(upload_to='bank_question_images/', null=True, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['bank', 'is_active', 'order']),
        ]
    
    def __str__(self) -> str:
        return self.text
    
    def get_choices(self) -> models.QuerySet:
        """Get question choices with caching."""
        cache_key = self.get_cache_key(f'bank_choices_{self.id}')
        choices = cache.get(cache_key)
        
        if choices is None:
            try:
                choices = list(self.choices.all())
                cache.set(cache_key, choices, CACHE_TTL)
                logger.debug(f'Successfully cached bank choices for question {self.id}')
                
            except Exception as e:
                logger.error(f'Error fetching bank choices: {str(e)}')
                return []
        
        return choices

class BankChoice(CachedMixin, models.Model):
    """Model for bank question choices."""
    question = models.ForeignKey(BankQuestion, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['question', 'is_correct']),
        ]
    
    def __str__(self) -> str:
        return self.text

# Signal handlers for cache invalidation
@receiver([post_save, post_delete], sender=QuestionBank)
def invalidate_bank_cache(sender, instance, **kwargs):
    """Invalidate bank-related caches."""
    try:
        instance.invalidate_cache()
        logger.debug(f'Successfully invalidated cache for bank {instance.id}')
    except Exception as e:
        logger.error(f'Error invalidating bank cache: {str(e)}')

@receiver([post_save, post_delete], sender=BankQuestion)
def invalidate_bank_question_cache(sender, instance, **kwargs):
    """Invalidate bank question-related caches."""
    try:
        instance.invalidate_cache()
        cache.delete_many([
            QuestionBank.get_cache_key(f'bank_questions_{instance.bank_id}'),
            BankQuestion.get_cache_key(f'bank_choices_{instance.id}')
        ])
        logger.debug(f'Successfully invalidated cache for bank question {instance.id}')
    except Exception as e:
        logger.error(f'Error invalidating bank question cache: {str(e)}')

@receiver([post_save, post_delete], sender=BankChoice)
def invalidate_bank_choice_cache(sender, instance, **kwargs):
    """Invalidate bank choice-related caches."""
    try:
        instance.invalidate_cache()
        cache.delete(BankQuestion.get_cache_key(f'bank_choices_{instance.question_id}'))
        logger.debug(f'Successfully invalidated cache for bank choice {instance.id}')
    except Exception as e:
        logger.error(f'Error invalidating bank choice cache: {str(e)}')
