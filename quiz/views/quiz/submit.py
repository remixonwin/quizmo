"""
Quiz submit view implemented with functional programming patterns.
"""
from typing import Dict, List, Optional, Any, Tuple
from django.views.generic import View
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.db.models import F, Sum
from ...utils.functional import (
    compose, pipe, memoize, safe_get,
    filter_none, map_queryset, validate_request,
    to_dict, immutable
)
from .base import QuizViewMixin
from ...models import Quiz, Question, Choice, QuizAttempt, UserAnswer
import logging
import json
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from decimal import Decimal

logger = logging.getLogger(__name__)

@immutable
class QuizSubmission:
    """Immutable quiz submission data structure."""
    
    def __init__(
        self,
        attempt: QuizAttempt,
        answers: List[Dict[str, Any]]
    ):
        # Use object.__setattr__ to bypass immutable restriction during initialization
        object.__setattr__(self, '_attempt', attempt)
        object.__setattr__(self, '_answers', answers)
        
    @property
    def attempt(self) -> QuizAttempt:
        return self._attempt
        
    @property
    def answers(self) -> List[Dict[str, Any]]:
        return self._answers.copy()

@method_decorator(csrf_protect, name='dispatch')
class QuizSubmitView(QuizViewMixin, View):
    """Handle quiz submission."""
    
    def post(self, request: HttpRequest, quiz_id: int) -> HttpResponse:
        """Process quiz submission."""
        try:
            logger.info(f'Processing quiz submission for quiz {quiz_id}')
            logger.debug(f'Content-Type: {request.content_type}')
            logger.debug(f'Request body: {request.body.decode("utf-8")}')
            
            # Validate user authentication and attempt
            if not request.user.is_authenticated:
                logger.warning('Unauthenticated user attempted to submit quiz')
                return HttpResponseBadRequest('Please log in to submit a quiz.')
                
            attempt = self.get_active_attempt(request.user, quiz_id)
            if not attempt:
                logger.warning(f'No active attempt found for user {request.user.id} on quiz {quiz_id}')
                return HttpResponseBadRequest('No active quiz attempt found.')
                
            if self.is_quiz_completed(request.user, quiz_id):
                logger.warning(f'User {request.user.id} attempted to submit already completed quiz {quiz_id}')
                return HttpResponseBadRequest('This quiz has already been completed.')
            
            try:
                # Extract answers
                answers = self._extract_answers(request)
                if not answers:
                    logger.warning(f'Missing or invalid answers for quiz {quiz_id} from user {request.user.id}')
                    return HttpResponseBadRequest('Please provide valid answers in JSON format: {"answers": [{"question_id": 1, "choice_id": 1}, ...]}')
                
                logger.info(f'Extracted {len(answers)} answers for quiz {quiz_id}')
                
                # Create immutable submission object
                submission = QuizSubmission(
                    attempt=attempt,
                    answers=answers
                )
                
                # Process submission using function composition
                process_submission = pipe(
                    self._create_submission,
                    self._validate_submission,
                    self._save_submission,
                    self._complete_attempt
                )
                
                # Process submission
                result = process_submission(submission)
                if not result:
                    logger.error(f'Failed to process submission for quiz {quiz_id} from user {request.user.id}')
                    return HttpResponseBadRequest('Error processing quiz submission. Please check your answers and try again.')
                
                # Clear cache
                self._clear_cache(quiz_id)
                
                logger.info(f'Successfully submitted quiz {quiz_id} for user {request.user.id}')
                messages.success(request, 'Quiz submitted successfully!')
                return redirect('quiz:quiz_results', quiz_id=quiz_id)
                
            except json.JSONDecodeError:
                logger.warning(f'Invalid JSON in request body for quiz {quiz_id}')
                return HttpResponseBadRequest('Invalid JSON format. Please provide answers in JSON format.')
                
            except Exception as e:
                logger.error(
                    f'Error in quiz submit for quiz {quiz_id} from user {request.user.id}: {str(e)}',
                    exc_info=True
                )
                return HttpResponseBadRequest(f'Error submitting quiz: {str(e)}')
            
        except Exception as e:
            logger.error(f'Failed to process submission for quiz {quiz_id} from user {request.user.id}', exc_info=True)
            return HttpResponseBadRequest(f'Error processing quiz: {str(e)}')
    
    def _extract_answers(
        self,
        request: HttpRequest
    ) -> List[Dict[str, Any]]:
        """Extract answers from request."""
        try:
            if not request.content_type == 'application/json':
                logger.warning('Invalid content type')
                return []
                
            data = json.loads(request.body)
            answers = data.get('answers', [])
            
            if not answers:
                logger.warning('No answers found in request body')
                return []
                
            # Validate answers format
            for answer in answers:
                if not all(k in answer for k in ['question_id', 'choice_id']):
                    logger.warning('Invalid answer format')
                    return []
                    
            return answers
            
        except json.JSONDecodeError:
            logger.warning('Invalid JSON in request body')
            return []
    
    def _create_submission(
        self,
        submission: QuizSubmission
    ) -> Optional[QuizSubmission]:
        """Validate and create submission object."""
        if not submission.answers:
            logger.error('No answers in submission')
            return None
            
        logger.info(f'Created submission with {len(submission.answers)} answers')
        return submission
    
    def _validate_submission(
        self,
        submission: Optional[QuizSubmission]
    ) -> Optional[QuizSubmission]:
        """Validate submission data."""
        if not submission:
            logger.error('Null submission in validate_submission')
            return None
            
        # Validate all answers have required fields
        valid_answers = all(
            safe_get(a, 'question_id') and safe_get(a, 'choice_id')
            for a in submission.answers
        )
        
        if not valid_answers:
            logger.error('Invalid answers in submission')
            return None
            
        # Validate question and choice IDs exist
        try:
            # Get all active questions for the quiz
            quiz_questions = submission.attempt.quiz.questions.filter(is_active=True)
            total_questions = quiz_questions.count()
            
            # Check if all questions are answered
            if len(submission.answers) != total_questions:
                logger.error(f'Missing answers: got {len(submission.answers)}, expected {total_questions}')
                return None
            
            # Validate each answer
            for answer in submission.answers:
                question_id = answer['question_id']
                choice_id = answer['choice_id']
                
                # Check if question exists and belongs to quiz
                question = quiz_questions.filter(id=question_id).first()
                if not question:
                    logger.error(f'Invalid question ID {question_id}')
                    return None
                    
                # Check if choice exists and belongs to question
                choice = question.choices.filter(id=choice_id).first()
                if not choice:
                    logger.error(f'Invalid choice ID {choice_id}')
                    return None
                    
                # Update is_correct flag based on actual choice
                answer['is_correct'] = choice.is_correct
                
            logger.info('Submission validation successful')
            return submission
            
        except Exception as e:
            logger.error(f'Error validating submission: {str(e)}', exc_info=True)
            return None
    
    @transaction.atomic
    def _save_submission(
        self,
        submission: Optional[QuizSubmission]
    ) -> Optional[QuizSubmission]:
        """Save submission answers."""
        if not submission:
            logger.error('Null submission in save_submission')
            return None
            
        try:
            # Create UserAnswer objects
            answers = [
                UserAnswer(
                    attempt=submission.attempt,
                    question_id=a['question_id'],
                    choice_id=a['choice_id']
                )
                for a in submission.answers
            ]
            
            # Bulk create answers
            UserAnswer.objects.bulk_create(answers)
            logger.info(f'Saved {len(answers)} answers')
            return submission
            
        except Exception as e:
            logger.error(f'Error saving submission: {str(e)}', exc_info=True)
            return None
    
    def _complete_attempt(
        self,
        submission: Optional[QuizSubmission]
    ) -> Optional[QuizSubmission]:
        """Complete quiz attempt."""
        if not submission:
            logger.error('Null submission in complete_attempt')
            return None
        
        try:
            attempt = submission.attempt
            now = timezone.now()
            
            # Get total questions from quiz
            quiz_questions = attempt.quiz.questions.filter(is_active=True)
            total_questions = quiz_questions.count()
            
            if total_questions == 0:
                logger.error(f'No active questions found for quiz {attempt.quiz.id}')
                return None
                
            total_points = quiz_questions.aggregate(total=Sum('points'))['total'] or 0
            
            # Validate total points
            if total_points <= 0:
                logger.error(f'Invalid total points ({total_points}) for quiz {attempt.quiz.id}')
                return None
            
            # Calculate score from saved answers
            correct_answers = 0
            earned_points = Decimal('0.0')
            
            # Group answers by difficulty for analytics
            difficulty_stats = {
                'easy': {'total': 0, 'correct': 0},
                'medium': {'total': 0, 'correct': 0},
                'hard': {'total': 0, 'correct': 0}
            }
            
            # Process each answer
            for answer in submission.answers:
                question = quiz_questions.get(id=answer['question_id'])
                
                # Skip inactive questions
                if not question.is_active:
                    continue
                    
                # Update difficulty stats
                difficulty = question.difficulty
                difficulty_stats[difficulty]['total'] += 1
                
                if answer.get('is_correct', False):
                    correct_answers += 1
                    earned_points += question.points
                    difficulty_stats[difficulty]['correct'] += 1
            
            # Calculate percentage score
            score = (earned_points / total_points * 100) if total_points > 0 else Decimal('0.0')
            
            # Round score to 2 decimal places
            score = round(score, 2)
            
            # Update attempt with detailed stats
            attempt.completed_at = now
            attempt.score = float(score)  # Convert to float for storage
            attempt.time_taken = (now - attempt.started_at).total_seconds()
            attempt.metadata = {
                'total_points': str(total_points),  # Store as string to preserve decimal precision
                'earned_points': str(earned_points),
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'difficulty_stats': difficulty_stats,
                'completion_time': attempt.time_taken
            }
            attempt.save()
            
            # Clear attempt from cache
            cache.delete(f'attempt_{attempt.user.id}_{attempt.quiz.id}')
            
            logger.info(
                f'Completed attempt {attempt.id} with score {score:.2f}% '
                f'({correct_answers}/{total_questions} correct, {earned_points:.1f}/{total_points:.1f} points) '
                f'in {attempt.time_taken:.1f} seconds'
            )
            
            return submission
            
        except Exception as e:
            logger.error(f'Error completing attempt: {str(e)}', exc_info=True)
            return None
    
    def _clear_cache(self, quiz_id: int) -> None:
        """Clear cached quiz data."""
        cache_keys = [
            f'quiz_take_{quiz_id}',
            f'quiz_results_{quiz_id}',
            f'quiz_view_{quiz_id}'
        ]
        cache.delete_many(cache_keys)
        logger.info(f'Cleared cache for quiz {quiz_id}')
    
    def handle_quiz_error(
        self,
        request: HttpRequest,
        message: str,
        redirect_url: str,
        **kwargs
    ) -> HttpResponseRedirect:
        """Handle quiz error with redirect."""
        messages.error(request, message)
        return redirect(redirect_url, **kwargs)

# Function-based view wrapper
view = QuizSubmitView.as_view()
