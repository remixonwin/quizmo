"""
Quiz start view.
"""
from django.views.generic import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from .base import QuizViewMixin
from ...models import Quiz, QuizAttempt
import logging

logger = logging.getLogger(__name__)

class QuizStartView(QuizViewMixin, View):
    """Handle starting a quiz."""
    
    def get(self, request: HttpRequest, quiz_id: int) -> HttpResponse:
        """Handle GET request to start quiz."""
        try:
            logger.info(f'Starting quiz {quiz_id} for user {request.user.id if request.user.is_authenticated else "anonymous"}')
            
            # Check authentication
            if not self.check_authentication(request):
                return redirect('quiz:quiz_list')
            
            # Get quiz with prefetched data
            quiz = get_object_or_404(
                Quiz.objects.prefetch_related('questions', 'questions__choices', 'bank'),
                id=quiz_id
            )
            logger.info(f'Found quiz {quiz.id}: {quiz.title}')
            
            # Check if quiz is active
            if not self.check_quiz_active(quiz):
                return redirect('quiz:quiz_list')
            
            # Check for existing attempts
            existing_attempt = self.get_active_attempt(request)
            if existing_attempt:
                logger.info(f'Found existing attempt {existing_attempt.id} for user {request.user.id}')
                
                if self.handle_timeout(existing_attempt):
                    logger.info(f'Attempt {existing_attempt.id} has timed out')
                    messages.warning(request, 'Your previous quiz timed out and has been submitted.')
                    return redirect('quiz:quiz_results', quiz_id=existing_attempt.quiz_id)
                
                if existing_attempt.quiz_id != quiz_id:
                    logger.warning(f'User has another quiz in progress: {existing_attempt.quiz_id}')
                    messages.error(request, 'You have another quiz in progress.')
                    return redirect('quiz:quiz_list')
                
                logger.info(f'Redirecting to existing attempt {existing_attempt.id}')
                return redirect('quiz:take_quiz', quiz_id=quiz_id)
            
            # Get or load questions
            questions = quiz.get_questions()
            if not questions:
                if quiz.bank:
                    logger.info(f'Loading questions from bank for quiz {quiz.id}')
                    questions = quiz.load_questions_from_bank()
                    if not questions:
                        return self.handle_quiz_error(
                            request,
                            'Failed to load quiz questions. Please try again.'
                        )
                else:
                    return self.handle_quiz_error(
                        request,
                        'This quiz has no questions available.'
                    )
            
            logger.info(f'Quiz {quiz.id} has {len(questions)} questions')
            
            # Create new attempt
            logger.info(f'Creating new attempt for quiz {quiz.id}')
            attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                started_at=timezone.now()
            )
            logger.info(f'Created attempt {attempt.id} for quiz {quiz.id}')
            
            return redirect('quiz:take_quiz', quiz_id=quiz_id)
            
        except Exception as e:
            return self.handle_quiz_error(
                request,
                f'An error occurred while starting the quiz: {str(e)}'
            )
