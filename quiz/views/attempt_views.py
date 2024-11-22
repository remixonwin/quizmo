"""
Views for handling quiz attempts, submissions, and results.
"""
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Prefetch, Count, Sum, F, Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from ..models import Quiz, Question, Choice, QuizAttempt, UserAnswer
from typing import Dict, List, Optional
from datetime import datetime, timedelta


QUIZ_TIMEOUT = getattr(settings, 'QUIZ_TIMEOUT_SECONDS', 2700)  # 45 minutes default
QUESTIONS_PER_PAGE = getattr(settings, 'QUESTIONS_PER_PAGE', 1)


def get_quiz_from_cache(quiz_id: int) -> Optional[Quiz]:
    """Get quiz from cache or database with optimized queries."""
    cache_key = f'quiz_detail_{quiz_id}'
    quiz = cache.get(cache_key)
    
    if quiz is None:
        try:
            quiz = Quiz.objects.select_related(
                'created_by'
            ).prefetch_related(
                Prefetch(
                    'questions',
                    queryset=Question.objects.prefetch_related(
                        Prefetch(
                            'choices',
                            queryset=Choice.objects.only('id', 'text', 'question_id', 'is_correct')
                        )
                    ).only('id', 'text', 'quiz_id', 'points')
                )
            ).get(pk=quiz_id, is_active=True)
            cache.set(cache_key, quiz, 300)  # Cache for 5 minutes
        except Quiz.DoesNotExist:
            return None
    return quiz


def clear_quiz_session(request) -> None:
    """Clear all quiz-related session data."""
    keys_to_clear = [k for k in request.session.keys() if k.startswith('quiz_')]
    for key in keys_to_clear:
        del request.session[key]
    request.session.modified = True


@login_required
def take_quiz(request, quiz_id: int):
    """Start or resume a quiz attempt with improved caching and pagination."""
    quiz = get_quiz_from_cache(quiz_id)
    if not quiz:
        messages.error(request, 'The requested quiz does not exist or is not active.')
        return HttpResponseRedirect(reverse('quiz:quiz_list'))
    
    # Use cached ongoing attempts
    cache_key = f'ongoing_attempt_{request.user.id}'
    ongoing_attempt = cache.get(cache_key)
    
    if ongoing_attempt is None:
        ongoing_attempt = QuizAttempt.objects.filter(
            user=request.user,
            completed_at__isnull=True
        ).select_related('quiz').first()
        cache.set(cache_key, ongoing_attempt, 300)
    
    if ongoing_attempt and ongoing_attempt.quiz_id != quiz_id:
        messages.warning(request, 'You have another quiz in progress. Please complete it first.')
        return HttpResponseBadRequest('Cannot start a new quiz while another is in progress')
    
    # Handle new attempt request
    if request.GET.get('start_new'):
        if ongoing_attempt:
            ongoing_attempt.delete()
            cache.delete(cache_key)
            messages.info(request, 'Previous attempt has been cleared.')
        clear_quiz_session(request)
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
            started_at=timezone.now()
        )
        cache.set(cache_key, attempt, 300)
        request.session[f'quiz_{quiz_id}_attempt'] = attempt.id
        request.session[f'quiz_{quiz_id}_start_time'] = attempt.started_at.timestamp()
        request.session.modified = True
        messages.success(request, 'New quiz attempt started.')
    
    # Validate session data
    attempt_id = request.session.get(f'quiz_{quiz_id}_attempt')
    start_time = request.session.get(f'quiz_{quiz_id}_start_time')
    
    if not attempt_id or not start_time:
        messages.warning(request, 'Quiz session expired. Starting new attempt.')
        return HttpResponseRedirect(
            reverse('quiz:take_quiz', kwargs={'quiz_id': quiz_id}) + '?start_new=1'
        )
    
    # Check timeout
    elapsed_time = timezone.now().timestamp() - float(start_time)
    if elapsed_time > QUIZ_TIMEOUT:
        messages.error(request, 'Quiz time limit exceeded. Your attempt has been submitted.')
        clear_quiz_session(request)
        if ongoing_attempt:
            ongoing_attempt.completed_at = timezone.now()
            ongoing_attempt.save()
            cache.delete(cache_key)
        return HttpResponseRedirect(reverse('quiz:quiz_results', kwargs={'quiz_id': quiz_id}))
    
    # Get current question with pagination
    page = int(request.GET.get('page', 1))
    answered_questions = request.session.get(f'quiz_{quiz_id}_answered', [])
    
    # Cache questions for better performance
    questions_cache_key = f'quiz_{quiz_id}_questions'
    questions = cache.get(questions_cache_key)
    
    if questions is None:
        questions = list(quiz.questions.exclude(id__in=answered_questions))
        cache.set(questions_cache_key, questions, 300)
    
    total_questions = len(questions)
    start_idx = (page - 1) * QUESTIONS_PER_PAGE
    end_idx = start_idx + QUESTIONS_PER_PAGE
    current_questions = questions[start_idx:end_idx] if start_idx < total_questions else []
    
    if not current_questions:
        if answered_questions:
            messages.success(request, 'All questions completed! Submitting your attempt.')
            return HttpResponseRedirect(
                reverse('quiz:submit_quiz', kwargs={'quiz_id': quiz_id})
            )
        messages.error(request, 'No questions available.')
        return HttpResponseRedirect(reverse('quiz:quiz_list'))
    
    return render(request, 'quiz/take_quiz.html', {
        'quiz': quiz,
        'questions': current_questions,
        'progress': len(answered_questions),
        'total_questions': total_questions,
        'time_remaining': max(0, QUIZ_TIMEOUT - int(elapsed_time)),
        'current_page': page,
        'total_pages': (total_questions + QUESTIONS_PER_PAGE - 1) // QUESTIONS_PER_PAGE,
        'page_title': f'Question {len(answered_questions) + 1}'
    })


@login_required
def submit_quiz(request, quiz_id: int):
    """Submit and grade a quiz attempt."""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return HttpResponseRedirect(reverse('quiz:quiz_list'))
    
    quiz = get_quiz_from_cache(quiz_id)
    if not quiz:
        messages.error(request, 'The requested quiz does not exist or is not active.')
        return HttpResponseRedirect(reverse('quiz:quiz_list'))
    
    attempt_id = request.session.get(f'quiz_{quiz_id}_attempt')
    
    if not attempt_id:
        messages.error(request, 'No active quiz attempt found.')
        return HttpResponseRedirect(reverse('quiz:quiz_list'))
    
    try:
        attempt = QuizAttempt.objects.get(
            id=attempt_id,
            user=request.user,
            completed_at__isnull=True
        )
    except QuizAttempt.DoesNotExist:
        messages.error(request, 'Quiz attempt not found or already completed.')
        clear_quiz_session(request)
        return HttpResponseRedirect(reverse('quiz:quiz_list'))
    
    # Process submitted answers
    try:
        answers = {}
        for key, value in request.POST.items():
            if key.startswith('question_') and value.isdigit():
                question_id = int(key.replace('question_', ''))
                choice_id = int(value)
                answers[question_id] = choice_id
        
        if not answers:
            messages.error(request, 'No answers were submitted.')
            return HttpResponseRedirect(reverse('quiz:take_quiz', kwargs={'quiz_id': quiz_id}))
        
        # Create UserAnswer objects
        user_answers = [
            UserAnswer(
                attempt=attempt,
                question_id=question_id,
                choice_id=choice_id
            ) for question_id, choice_id in answers.items()
        ]
        UserAnswer.objects.bulk_create(user_answers)
        
        # Mark attempt as completed
        attempt.completed_at = timezone.now()
        attempt.save()
        
        # Clear session data
        clear_quiz_session(request)
        
        messages.success(request, 'Quiz submitted successfully!')
        return HttpResponseRedirect(
            reverse('quiz:quiz_results', kwargs={'quiz_id': quiz_id})
        )
    except Exception as e:
        messages.error(request, f'An error occurred while submitting your quiz: {str(e)}')
        return HttpResponseRedirect(reverse('quiz:take_quiz', kwargs={'quiz_id': quiz_id}))


@login_required
def quiz_results(request, quiz_id: int):
    """Display quiz results with detailed feedback and improved caching."""
    cache_key = f'quiz_results_{quiz_id}_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        quiz = get_quiz_from_cache(quiz_id)
        if not quiz:
            messages.error(request, 'Quiz not found.')
            return HttpResponseRedirect(reverse('quiz:quiz_list'))
        
        latest_attempt = QuizAttempt.objects.filter(
            quiz=quiz,
            user=request.user,
            completed_at__isnull=False
        ).select_related(
            'quiz'
        ).prefetch_related(
            Prefetch(
                'useranswer_set',
                queryset=UserAnswer.objects.select_related(
                    'question',
                    'choice'
                ).prefetch_related(
                    'question__choices'
                )
            )
        ).annotate(
            total_points=Sum('useranswer__points'),
            correct_answers=Count(
                'useranswer',
                filter=Q(useranswer__is_correct=True)
            )
        ).order_by('-completed_at').first()
        
        if not latest_attempt:
            messages.error(request, 'No completed quiz attempt found.')
            return HttpResponseRedirect(reverse('quiz:quiz_list'))
        
        cached_data = {
            'quiz': quiz,
            'attempt': latest_attempt,
            'user_answers': list(latest_attempt.useranswer_set.all())
        }
        cache.set(cache_key, cached_data, 600)  # Cache for 10 minutes
    
    return render(request, 'quiz/quiz_results.html', {
        'quiz': cached_data['quiz'],
        'attempt': cached_data['attempt'],
        'user_answers': cached_data['user_answers'],
        'page_title': f'Results: {cached_data["quiz"].title}'
    })
