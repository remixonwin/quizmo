"""
Signal handlers for the quiz app.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import Quiz, Question, QuizAttempt
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=Quiz)
def invalidate_quiz_cache(sender, instance, created, **kwargs):
    """Invalidate quiz-related cache when a quiz is saved."""
    try:
        cache_keys = [
            f'quiz_{instance.id}',
            'quiz_list',
            f'quiz_questions_{instance.id}',
            f'quiz_stats_{instance.id}'
        ]
        cache.delete_many(cache_keys)
        logger.info(f"{'Created' if created else 'Updated'} quiz cache invalidated for quiz {instance.id}")
    except Exception as e:
        logger.error(f"Error invalidating quiz cache: {e}")

@receiver(post_delete, sender=Quiz)
def cleanup_quiz_cache(sender, instance, **kwargs):
    """Clean up quiz-related cache when a quiz is deleted."""
    try:
        cache_keys = [
            f'quiz_{instance.id}',
            'quiz_list',
            f'quiz_questions_{instance.id}',
            f'quiz_stats_{instance.id}'
        ]
        cache.delete_many(cache_keys)
        logger.info(f"Deleted quiz cache cleaned up for quiz {instance.id}")
    except Exception as e:
        logger.error(f"Error cleaning up quiz cache: {e}")

@receiver(post_save, sender=Question)
def invalidate_question_cache(sender, instance, created, **kwargs):
    """Invalidate question-related cache when a question is saved."""
    try:
        cache_keys = [
            f'question_{instance.id}',
            f'quiz_questions_{instance.quiz_id}',
            f'quiz_stats_{instance.quiz_id}'
        ]
        cache.delete_many(cache_keys)
        logger.info(f"{'Created' if created else 'Updated'} question cache invalidated for question {instance.id}")
    except Exception as e:
        logger.error(f"Error invalidating question cache: {e}")

@receiver(post_save, sender=QuizAttempt)
def update_user_stats(sender, instance, created, **kwargs):
    """Update user statistics when a quiz attempt is saved."""
    try:
        if created:
            # Invalidate user stats cache
            cache_keys = [
                f'user_stats_{instance.user_id}',
                f'quiz_stats_{instance.quiz_id}',
                f'user_recent_attempts_{instance.user_id}'
            ]
            cache.delete_many(cache_keys)
            
            # Update user's last activity
            User.objects.filter(id=instance.user_id).update(last_activity=instance.completed_at)
            
            logger.info(f"User stats updated for user {instance.user_id}, quiz {instance.quiz_id}")
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")

@receiver(post_delete, sender=QuizAttempt)
def cleanup_attempt_cache(sender, instance, **kwargs):
    """Clean up cache when a quiz attempt is deleted."""
    try:
        cache_keys = [
            f'user_stats_{instance.user_id}',
            f'quiz_stats_{instance.quiz_id}',
            f'user_recent_attempts_{instance.user_id}'
        ]
        cache.delete_many(cache_keys)
        logger.info(f"Quiz attempt cache cleaned up for user {instance.user_id}, quiz {instance.quiz_id}")
    except Exception as e:
        logger.error(f"Error cleaning up quiz attempt cache: {e}")
