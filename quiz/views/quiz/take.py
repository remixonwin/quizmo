"""
Quiz take view.
"""
from typing import Dict, Any, List, Optional
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.core.cache import cache
from django.db.models import Prefetch
from .base import QuizViewMixin
from ...models import Quiz, Question, Choice, QuizAttempt
import logging
import random

logger = logging.getLogger(__name__)

class QuizTakeView(LoginRequiredMixin, QuizViewMixin, DetailView):
    """View for taking a quiz."""
    template_name = 'quiz/quiz_take.html'
    context_object_name = 'quiz'
    model = Quiz
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Handle GET request."""
        quiz = self.get_object()
        
        # Check if user has an active attempt
        attempt = self.get_active_attempt(request.user, quiz.id)
        if not attempt:
            # No active attempt, redirect to start
            return redirect('quiz:quiz_start', pk=quiz.id)
        
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
                quiz.questions.filter(
                    is_active=True
                ).prefetch_related(
                    Prefetch(
                        'choices',
                        queryset=Choice.objects.filter(
                            is_active=True
                        ).order_by('?')
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
