"""
Quiz take view implemented using functional programming patterns.
"""
from typing import Dict, List, Optional, Any
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.db.models import Prefetch
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.cache import cache
from ...utils.functional import (
    compose, pipe, memoize, safe_get, 
    filter_none, map_queryset, validate_request
)
from .base import QuizViewMixin
from ...models import Quiz, Question, Choice
import logging

logger = logging.getLogger(__name__)

@login_required
def view(request: HttpRequest, quiz_id: int) -> HttpResponse:
    """Function-based view for taking a quiz."""
    # Initialize quiz view helper
    quiz_view = QuizViewMixin()
    
    # Get quiz from cache or database
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Get existing attempt or validate new attempt
    attempt = quiz_view.get_active_attempt(request.user, quiz_id)
    if not attempt:
        # Validate quiz access for new attempt
        if not quiz_view.can_start_quiz(request.user, quiz_id):
            return quiz_view.handle_quiz_error(
                request,
                'You cannot access this quiz.'
            )
        # Create new attempt
        attempt = quiz_view.get_or_create_attempt(request.user, quiz_id)
        if not attempt:
            return quiz_view.handle_quiz_error(
                request,
                'Could not create quiz attempt.'
            )
    
    # Check time limit
    time_check = quiz_view.check_time_limit(attempt, request)
    if isinstance(time_check, HttpResponseRedirect):
        return time_check
    
    # Load questions from database
    questions = Question.objects.prefetch_related(
        Prefetch(
            'choices',
            queryset=Choice.objects.filter(is_active=True).order_by('order')
        )
    ).filter(
        quiz=quiz,
        is_active=True
    ).order_by('order')
    
    # Load quiz data from cache
    cache_key = f'quiz_data_{quiz_id}'
    quiz_data = cache.get(cache_key)
    
    if not quiz_data:
        # Format quiz data
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'passing_score': quiz.pass_mark,
            'time_limit': quiz.time_limit,
            'randomize_questions': quiz.randomize_questions,
            'show_answers': quiz.show_answers
        }
        
        # Cache quiz data
        cache.set(cache_key, quiz_data, timeout=3600)  # Cache for 1 hour
    
    # Format time remaining as MM:SS
    time_remaining = quiz_view.get_remaining_time(attempt)
    minutes = time_remaining // 60
    seconds = time_remaining % 60
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    # Prepare context
    context = {
        'quiz': quiz_data,
        'questions': questions,
        'attempt': attempt,
        'time_remaining': time_str,
        'progress': 0  # TODO: Calculate progress
    }
    
    return render(request, 'quiz/take_quiz.html', context)
