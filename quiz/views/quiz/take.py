"""
Quiz take view.
"""
from typing import Dict, Any, List, Optional
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.cache import cache
from django.db.models import Prefetch
from .base import QuizViewMixin
from ...models import Quiz, Question, Choice, QuizAttempt, QuizAnswer
import logging
import random
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.shortcuts import render

logger = logging.getLogger(__name__)

class QuizTakeView(LoginRequiredMixin, QuizViewMixin, DetailView):
    """View for taking a quiz."""
    template_name = 'quiz/quiz_take.html'
    context_object_name = 'quiz'
    model = Quiz
    pk_url_kwarg = 'quiz_id'
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Handle GET request."""
        quiz = self.get_object()
        
        # Check if user has an active attempt
        attempt = self.get_active_attempt(request.user, quiz.id)
        if not attempt:
            # No active attempt, redirect to start
            return redirect('quiz:quiz_start', quiz_id=quiz.id)
        
        # Get or generate questions
        questions = self.get_questions(quiz, attempt)
        if not questions:
            logger.error(f'No questions found for quiz {quiz.id}')
            return redirect('quiz:quiz_list')
        
        # Get current question index from session, default to 0
        current_question = int(request.GET.get('question', 0))
        if current_question >= len(questions):
            current_question = 0
        
        # Add questions to context
        self.questions = questions
        self.current_question = current_question
        return super().get(request, *args, **kwargs)
    
    def get_questions(self, quiz: Quiz, attempt: QuizAttempt) -> List[Question]:
        """Get questions for the quiz attempt."""
        # Try to get cached questions
        cache_key = f'questions_{attempt.id}'
        questions = cache.get(cache_key)
        
        if not questions:
            # Get all active questions with choices
            questions = list(
                quiz.questions.prefetch_related(
                    Prefetch(
                        'choices',
                        queryset=Choice.objects.order_by('?')
                    )
                ).order_by('order')
            )
            
            # Log question count
            logger.info(f'Found {len(questions)} questions for quiz {quiz.id}')
            
            # Ensure we have exactly 40 questions
            if len(questions) > 40:
                # Randomly select 40 questions if we have more
                questions = random.sample(questions, 40)
            elif len(questions) < 40:
                logger.warning(
                    f'Quiz {quiz.id} has fewer than 40 questions ({len(questions)})'
                )
            
            # Randomize question order
            random.shuffle(questions)
            
            # Cache questions
            cache.set(cache_key, questions, timeout=3600)  # Cache for 1 hour
        
        return questions
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add questions to context."""
        context = super().get_context_data(**kwargs)
        quiz = self.object
        
        # Get active attempt
        attempt = self.get_active_attempt(self.request.user, quiz.id)
        
        # Get current question
        current_question = self.questions[self.current_question]
        next_question = self.current_question + 1 if self.current_question < len(self.questions) - 1 else None
        prev_question = self.current_question - 1 if self.current_question > 0 else None
        
        context.update({
            'attempt': attempt,
            'current_question': current_question,
            'question_number': self.current_question + 1,
            'next_question': next_question,
            'prev_question': prev_question,
            'total_questions': len(self.questions),
            'required_correct': 32,
            'time_remaining': attempt.time_remaining if attempt else quiz.time_limit * 60
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        try:
            # Parse JSON data
            data = json.loads(request.body)
            answers = data.get('answers', [])
            metadata = data.get('metadata', {})
            
            # Get quiz and attempt
            quiz = self.get_object()
            attempt = self.get_active_attempt(request.user, quiz.id)
            
            # Save answers
            for answer in answers:
                question_id = answer.get('question_id')
                choice_id = answer.get('choice_id')
                
                if not question_id or not choice_id:
                    return JsonResponse({
                        'error': 'Invalid answer format: missing question_id or choice_id'
                    }, status=400)
                
                # Validate question belongs to quiz
                question = get_object_or_404(Question, id=question_id, quiz=quiz)
                choice = get_object_or_404(Choice, id=choice_id, question=question)
                
                # Save answer
                QuizAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'choice': choice}
                )
            
            # Calculate score
            total_questions = quiz.questions.count()
            correct_answers = QuizAnswer.objects.filter(
                attempt=attempt,
                choice__is_correct=True
            ).count()
            
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            # Complete attempt
            attempt.score = score
            attempt.completed_at = timezone.now()
            attempt.save()
            
            return JsonResponse({
                'success': True,
                'score': float(score),
                'redirect_url': reverse('quiz:quiz_results', kwargs={'quiz_id': quiz.id})
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f'Error processing quiz submission: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': 'An unexpected error occurred'
            }, status=500)
