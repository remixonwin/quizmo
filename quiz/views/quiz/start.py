"""
Quiz start view.
"""
from django.views.generic import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .base import QuizViewMixin
from ...models import Quiz, QuizAttempt
import logging

logger = logging.getLogger(__name__)

class QuizStartView(LoginRequiredMixin, QuizViewMixin, View):
    """Handle starting a quiz."""
    
    def get(self, request: HttpRequest, quiz_id: int) -> HttpResponse:
        """Handle GET request to start quiz."""
        try:
            logger.info(f'Starting quiz {quiz_id} for user {request.user.id}')
            
            # Get quiz with prefetched data
            quiz = get_object_or_404(
                Quiz.objects.prefetch_related('questions', 'questions__choices'),
                id=quiz_id
            )
            logger.info(f'Found quiz {quiz.id}: {quiz.title}')
            
            # Check if quiz is active
            if not quiz.is_active:
                messages.error(request, 'This quiz is not currently available.')
                return redirect('quiz:quiz_list')
            
            # Check for existing attempts
            existing_attempt = self.get_active_attempt(request.user, quiz_id)
            if existing_attempt:
                logger.info(f'Found existing attempt {existing_attempt.id} for user {request.user.id}')
                
                # Check for timeout
                if self.handle_timeout(existing_attempt):
                    logger.info(f'Attempt {existing_attempt.id} has timed out')
                    messages.warning(request, 'Your previous quiz timed out and has been submitted.')
                    return redirect('quiz:quiz_results', quiz_id=existing_attempt.quiz_id)
                
                # Check for attempt on different quiz
                if existing_attempt.quiz_id != quiz_id:
                    logger.warning(f'User has another quiz in progress: {existing_attempt.quiz_id}')
                    messages.error(request, 'You have another quiz in progress.')
                    return redirect('quiz:quiz_list')
                
                # Continue existing attempt
                logger.info(f'Redirecting to existing attempt {existing_attempt.id}')
                return redirect('quiz:quiz_take', quiz_id=quiz_id)
            
            # Get questions
            questions = quiz.questions.filter(is_active=True)
            if not questions.exists():
                return self.handle_quiz_error(
                    request,
                    'This quiz has no questions available.'
                )
            
            logger.info(f'Quiz {quiz.id} has {questions.count()} questions')
            
            # Create new attempt
            logger.info(f'Creating new attempt for quiz {quiz.id}')
            attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                started_at=timezone.now(),
                metadata={
                    'total_points': '0.0',
                    'earned_points': '0.0',
                    'correct_answers': 0,
                    'total_questions': 0,
                    'difficulty_stats': {
                        'easy': {'total': 0, 'correct': 0},
                        'medium': {'total': 0, 'correct': 0},
                        'hard': {'total': 0, 'correct': 0}
                    },
                    'completion_time': 0.0
                }
            )
            logger.info(f'Created attempt {attempt.id} for quiz {quiz.id}')
            
            return redirect('quiz:quiz_take', quiz_id=quiz_id)
            
        except Exception as e:
            return self.handle_quiz_error(
                request,
                f'An error occurred while starting the quiz: {str(e)}'
            )
    
    def post(self, request: HttpRequest, quiz_id: int) -> HttpResponse:
        """Handle POST request to start quiz."""
        try:
            logger.info(f'Starting quiz {quiz_id} for user {request.user.id}')
            
            # Get quiz
            quiz = get_object_or_404(Quiz, id=quiz_id)
            
            # Check if quiz is active
            if not quiz.is_active:
                messages.error(request, 'This quiz is not currently available.')
                return redirect('quiz:quiz_list')
            
            # Create new attempt
            attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                started_at=timezone.now(),
                metadata={
                    'total_points': '0.0',
                    'earned_points': '0.0',
                    'correct_answers': 0,
                    'total_questions': 0,
                    'difficulty_stats': {
                        'easy': {'total': 0, 'correct': 0},
                        'medium': {'total': 0, 'correct': 0},
                        'hard': {'total': 0, 'correct': 0}
                    },
                    'completion_time': 0.0
                }
            )
            logger.info(f'Created attempt {attempt.id} for quiz {quiz.id}')
            
            return redirect('quiz:quiz_take', quiz_id=quiz_id)
            
        except Exception as e:
            return self.handle_quiz_error(
                request,
                f'An error occurred while starting the quiz: {str(e)}'
            )
