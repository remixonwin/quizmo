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
from ...models import Quiz, Question, Choice, QuizAttempt, QuizAnswer
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
    
    def post(self, request, *args, **kwargs):
        """Handle quiz submission."""
        logger.info(f'Quiz submission received for quiz {self.kwargs["quiz_id"]}')
        
        # Verify content type
        if request.content_type != 'application/json':
            logger.error(f'Invalid content type: {request.content_type}')
            return JsonResponse({'error': 'Content-Type must be application/json'}, status=400)
        
        try:
            # Get quiz and validate it exists
            quiz = self.get_quiz()
            if not quiz:
                logger.error('Quiz not found')
                return JsonResponse({'error': 'Quiz not found'}, status=404)
            
            # Get or create attempt
            attempt = self.get_or_create_attempt(quiz)
            if not attempt:
                logger.error('Could not get or create attempt')
                return JsonResponse({'error': 'Could not create attempt'}, status=400)
            
            # Extract answers from request
            try:
                answers, metadata = self._extract_answers(request)
                if not answers:
                    logger.error('No answers provided in submission')
                    return JsonResponse({'error': 'No answers provided'}, status=400)
            except ValueError as e:
                logger.error(f'Invalid answers format: {str(e)}')
                return JsonResponse({'error': str(e)}, status=400)
            
            # Validate answers
            try:
                self._validate_answers(quiz, answers)
            except ValueError as e:
                logger.error(f'Answer validation failed: {str(e)}')
                return JsonResponse({'error': str(e)}, status=400)
            
            # Save answers
            try:
                with transaction.atomic():
                    self._save_answers(attempt, answers)
                    self._update_attempt_metadata(attempt, metadata)
            except Exception as e:
                logger.error(f'Error saving answers: {str(e)}')
                return JsonResponse({'error': 'Error saving answers'}, status=500)
            
            # Calculate score
            try:
                score = self._calculate_score(attempt, answers)
                attempt.score = score
                attempt.completed_at = timezone.now()
                attempt.save()
            except Exception as e:
                logger.error(f'Error calculating score: {str(e)}')
                return JsonResponse({'error': 'Error calculating score'}, status=500)
            
            logger.info(f'Quiz submission successful. Score: {score}')
            return JsonResponse({
                'success': True,
                'score': float(score),
                'redirect_url': reverse('quiz:quiz_results', kwargs={'quiz_id': quiz.id})
            })
            
        except Exception as e:
            logger.error(f'Unexpected error in quiz submission: {str(e)}', exc_info=True)
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
            
    def get_quiz(self):
        """Get quiz by ID."""
        return get_object_or_404(Quiz, id=self.kwargs['quiz_id'])
    
    def get_or_create_attempt(self, quiz):
        """Get or create quiz attempt."""
        attempt = QuizAttempt.objects.filter(
            user=self.request.user,
            quiz=quiz,
            completed_at__isnull=True
        ).order_by('-started_at').first()
        
        if not attempt:
            attempt = QuizAttempt.objects.create(
                user=self.request.user,
                quiz=quiz,
                started_at=timezone.now()
            )
        
        return attempt
    
    def _extract_answers(self, request):
        """Extract answers from request data."""
        try:
            logger.info(f'Extracting answers from request. Content-Type: {request.content_type}')
            body = request.body.decode('utf-8') if request.body else None
            logger.info(f'Request body: {body}')
            
            if not body:
                raise ValueError('No data provided')
            
            # Parse JSON data from request body
            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error(f'JSON decode error: {str(e)}')
                raise ValueError(f'Invalid JSON format: {str(e)}')
            
            logger.info(f'Parsed request data: {data}')
            
            if not isinstance(data, dict):
                raise ValueError('Request data must be a JSON object')
            
            answers = data.get('answers')
            metadata = data.get('metadata', {})
            
            if not answers:
                raise ValueError('No answers provided')
            
            if not isinstance(answers, list):
                raise ValueError('Answers must be a list')
            
            logger.info(f'Processing {len(answers)} answers')
            
            # Validate answer format
            for i, answer in enumerate(answers):
                if not isinstance(answer, dict):
                    raise ValueError(f'Answer {i} must be a dictionary')
                if 'question_id' not in answer:
                    raise ValueError(f'Answer {i} missing question_id')
                if 'choice_id' not in answer:
                    raise ValueError(f'Answer {i} missing choice_id')
                
                # Convert IDs to integers
                try:
                    answer['question_id'] = int(answer['question_id'])
                    answer['choice_id'] = int(answer['choice_id'])
                except (TypeError, ValueError):
                    raise ValueError(f'Answer {i} has invalid ID format')
            
            logger.info('Answer validation successful')
            return answers, metadata
            
        except Exception as e:
            logger.error(f'Error extracting answers: {str(e)}', exc_info=True)
            raise
    
    def _validate_answers(self, quiz, answers):
        """Validate answers."""
        active_questions = quiz.questions.filter(is_active=True)
        active_question_ids = set(active_questions.values_list('id', flat=True))
        
        for answer in answers:
            if answer['question_id'] not in active_question_ids:
                raise ValueError('Invalid question ID')
            
            question = active_questions.get(id=answer['question_id'])
            choice = question.choices.get(id=answer['choice_id'])
            
            if not choice:
                raise ValueError('Invalid choice ID')
    
    @transaction.atomic
    def _save_answers(self, attempt: QuizAttempt, answers: List[Dict[str, Any]]) -> None:
        """Save answers to database."""
        # Delete any existing answers for this attempt
        attempt.answers.all().delete()
        
        # Create new answers
        for answer in answers:
            question = get_object_or_404(Question, id=answer['question_id'])
            choice = get_object_or_404(Choice, id=answer['choice_id'])
            
            QuizAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={'choice': choice}
            )
    
    def _update_attempt_metadata(self, attempt, metadata):
        """Update attempt metadata."""
        attempt.metadata = {
            **attempt.metadata,
            **metadata,
            'completion_time': (timezone.now() - attempt.started_at).total_seconds()
        }
        attempt.save()
    
    def _calculate_score(self, attempt, answers):
        """Calculate score for quiz attempt."""
        # Get active questions and answers
        active_questions = attempt.quiz.questions.filter(is_active=True)
        correct_answers = 0
        total_points = 0
        
        for answer in answers:
            question = active_questions.get(id=answer['question_id'])
            choice = question.choices.get(id=answer['choice_id'])
            points = question.points or 1.0
            total_points += points
            
            if choice.is_correct:
                correct_answers += 1
        
        # Calculate final score
        if total_points > 0:
            score = (correct_answers / len(active_questions)) * 100
        else:
            score = 0
        
        attempt.correct_answers = correct_answers
        attempt.save()
        
        return score
