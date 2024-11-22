"""
Quiz submit view implemented with functional programming patterns.
"""
from typing import Dict, List, Optional, Any, Tuple
from django.views.generic import View
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.db.models import F, Sum
from django.utils.dateparse import parse_datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
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
from collections import defaultdict

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
class QuizSubmitView(LoginRequiredMixin, QuizViewMixin, View):
    """View for submitting quiz answers."""
    
    def post(self, request: HttpRequest, pk: int, api: bool = False) -> HttpResponse:
        """Handle quiz submission."""
        try:
            # Get quiz
            quiz = get_object_or_404(Quiz, id=pk)
            
            # Validate quiz is active
            if not quiz.is_active:
                return self.error_response('Quiz is not active', 400)
            
            # Get or validate answers
            try:
                answers, metadata = self._extract_answers(request)
            except ValueError as e:
                logger.error(f'Error extracting answers: {str(e)}')
                return self.error_response(str(e), 400)
                
            if not answers:
                logger.error('No answers provided in submission')
                return self.error_response('No answers provided', 400)
            
            # Get active questions for this quiz
            active_questions = quiz.questions.filter(is_active=True)
            
            # Get or create quiz attempt
            attempt = QuizAttempt.objects.filter(
                user=request.user,
                quiz=quiz,
                completed_at__isnull=True
            ).order_by('-started_at').first()
            
            if not attempt:
                attempt = QuizAttempt.objects.create(
                    user=request.user,
                    quiz=quiz,
                    started_at=timezone.now()
                )
            
            # Check time limit if set
            time_elapsed = timezone.now() - attempt.started_at
            time_limit_minutes = quiz.time_limit or 0
            if time_limit_minutes > 0:
                time_elapsed_minutes = time_elapsed.total_seconds() / 60
                if time_elapsed_minutes > time_limit_minutes:
                    return self.error_response(f'Time limit of {time_limit_minutes} minutes exceeded', 400)
            
            # Filter answers to only include active questions
            active_question_ids = set(active_questions.values_list('id', flat=True))
            try:
                active_answers = [answer for answer in answers if answer['question_id'] in active_question_ids]
            except KeyError:
                return self.error_response('Invalid answer format: missing question_id', 400)
            
            # Validate all required questions are answered
            if len(active_answers) < len(active_question_ids):
                msg = f'Incomplete submission. Expected {len(active_question_ids)} answers, got {len(active_answers)}.'
                logger.warning(f'Incomplete submission for quiz {quiz.id} from user {request.user.id}. {msg}')
                return self.error_response(msg, 400)
            
            # Validate answers
            for answer in active_answers:
                try:
                    question = active_questions.get(id=answer['question_id'])
                    choice = question.choices.get(id=answer['choice_id'])
                except (Question.DoesNotExist, Choice.DoesNotExist):
                    return self.error_response('Invalid question or choice ID', 400)
                except KeyError:
                    return self.error_response('Invalid answer format: missing required fields', 400)
            
            # Save answers
            self._save_answers(attempt, active_answers)
            
            # Calculate score
            score = self._calculate_score(attempt)
            
            # Update attempt metadata
            attempt.metadata = {
                **attempt.metadata,
                **metadata,
                'completion_time': time_elapsed.total_seconds()
            }
            attempt.completed_at = timezone.now()
            attempt.score = score
            attempt.save()
            
            # Log success
            logger.info(
                f'Quiz {quiz.id} submitted successfully by user {request.user.id}. '
                f'Score: {score:.2f}%, Time: {attempt.metadata["completion_time"]:.2f}s'
            )
            
            # Return response based on whether this is an API request
            if api:
                return JsonResponse({
                    'score': float(score),
                    'correct_answers': attempt.correct_answers,
                    'total_questions': len(active_questions),
                    'completion_time': attempt.metadata['completion_time']
                })
            else:
                messages.success(request, f'Quiz submitted successfully! Score: {score:.2f}%')
                return redirect('quiz:quiz_results', pk=attempt.id)
                
        except Exception as e:
            logger.error('Error processing quiz submission', exc_info=True)
            return self.error_response('Error processing quiz submission', 500)
            
    def error_response(self, message: str, status: int) -> HttpResponse:
        """Return error response based on whether this is an API request."""
        if getattr(self.request, 'api', False):
            return JsonResponse({'error': message}, status=status)
        else:
            if status == 400:
                # For validation errors, return 400 status code with JSON
                return JsonResponse({'error': message}, status=status)
            else:
                # For other errors, redirect with message
                messages.error(self.request, message)
                return redirect('quiz:quiz_take', pk=self.kwargs['pk'])
    
    def _extract_answers(self, request):
        """Extract answers from request data."""
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))
                answers = data.get('answers', [])
                metadata = data.get('metadata', {})
            else:
                answers = json.loads(request.POST.get('answers', '[]'))
                metadata = json.loads(request.POST.get('metadata', '{}'))
            
            if not answers:
                raise ValueError('No answers provided')
                
            # Validate answer format
            for answer in answers:
                if not isinstance(answer, dict):
                    raise ValueError('Invalid answer format: each answer must be a dictionary')
                if 'question_id' not in answer:
                    raise ValueError('Invalid answer format: missing question_id')
                if 'choice_id' not in answer:
                    raise ValueError('Invalid answer format: missing choice_id')
                if not isinstance(answer['question_id'], int):
                    raise ValueError('Invalid answer format: question_id must be an integer')
                if not isinstance(answer['choice_id'], int):
                    raise ValueError('Invalid answer format: choice_id must be an integer')
            
            return answers, metadata
        except json.JSONDecodeError:
            raise ValueError('Invalid JSON format for answers')
    
    @transaction.atomic
    def _save_answers(self, attempt: QuizAttempt, answers: List[Dict[str, Any]]) -> None:
        """Save answers to database."""
        # Delete any existing answers for this attempt
        attempt.answers.all().delete()
        
        # Create new answers
        UserAnswer.objects.bulk_create([
            UserAnswer(
                attempt=attempt,
                question_id=answer['question_id'],
                choice_id=answer['choice_id']
            )
            for answer in answers
        ])
    
    def _calculate_score(self, attempt: QuizAttempt) -> float:
        """Calculate score for quiz attempt."""
        # Get active questions and answers
        active_questions = attempt.quiz.questions.filter(is_active=True)
        answers = attempt.answers.all()
        
        # Calculate score
        score = 0
        total_points = 0
        correct_answers = 0
        
        for answer in answers:
            question = active_questions.get(id=answer.question_id)
            choice = question.choices.get(id=answer.choice_id)
            points = question.points or 1.0
            total_points += points
            
            if choice.is_correct:
                score += points
                correct_answers += 1
        
        # Calculate final score
        if total_points > 0:
            score = (score / total_points) * 100
        
        attempt.correct_answers = correct_answers
        attempt.save()
        
        return score
