# Standard library imports
import time
import logging
import threading
import json
import datetime
from datetime import timedelta
import os
import psutil
import socket
from django.conf import settings
from django.core.cache import cache

# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Prefetch, Count, Q, F, Value, FloatField, Max
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django import forms
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.views.decorators.cache import cache_page, never_cache
from django.db import transaction, connections, connection, OperationalError
from django.views.decorators.vary import vary_on_cookie
from redis.exceptions import RedisError
from django.views.decorators.http import require_GET

# Configure logger
browser_logger = logging.getLogger('browser_errors')
browser_logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler('browser-errors.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
browser_logger.addHandler(file_handler)

# Configure logging for health checks
health_logger = logging.getLogger('health_checks')
health_logger.setLevel(logging.DEBUG)  # Set to DEBUG for more verbose logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(process)d] %(message)s')
handler.setFormatter(formatter)
health_logger.addHandler(handler)

# Track application startup time - ensure this is module level
STARTUP_TIME = time.time()
STARTUP_GRACE_PERIOD = 90  # seconds
DB_TIMEOUT = 5  # seconds

# Lock for thread-safe database operations
db_lock = threading.Lock()

def get_system_metrics():
    """Gather system metrics for diagnostics."""
    try:
        process = psutil.Process(os.getpid())
        metrics = {
            'memory_percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent(),
            'threads': process.num_threads(),
            'open_files': len(process.open_files()),
            'connections': len(process.connections()),
            'hostname': socket.gethostname(),
            'worker_pid': os.getpid(),
            'worker_ppid': os.getppid()
        }
        return metrics
    except Exception as e:
        health_logger.error(f"Failed to gather system metrics: {str(e)}", exc_info=True)
        return {}

def check_redis_connection():
    """Check Redis connection status."""
    try:
        cache.set('health_check_test', 'test', timeout=10)
        result = cache.get('health_check_test')
        return result == 'test', None
    except Exception as e:
        return False, f"Redis connection failed: {str(e)}"

def get_database_metrics():
    """Get database connection metrics."""
    try:
        from django.db import connections
        db_metrics = {}
        for alias in connections:
            conn = connections[alias]
            db_metrics[alias] = {
                'vendor': conn.vendor,
                'is_usable': conn.is_usable(),
                'allow_thread_sharing': conn.allow_thread_sharing,
                'settings': {
                    k: v for k, v in conn.settings_dict.items() 
                    if k not in ('PASSWORD', 'USER', 'NAME')  # Exclude sensitive info
                }
            }
        return db_metrics
    except Exception as e:
        health_logger.error(f"Failed to gather database metrics: {str(e)}", exc_info=True)
        return {}

def check_database():
    """Thread-safe database check with connection reset on failure."""
    with db_lock:
        health_logger.debug(f'Database check started. Process ID: {os.getpid()}')
        metrics = get_system_metrics()
        db_metrics = get_database_metrics()
        health_logger.debug(f'System metrics: {metrics}')
        health_logger.debug(f'Database metrics: {db_metrics}')
        
        try:
            health_logger.debug('Attempting database connection check')
            health_logger.debug(f'Connection state before check: {connection.connection is not None}')
            
            # Track connection attempt timing
            start_time = time.time()
            connection.ensure_connection()
            ensure_time = time.time() - start_time
            health_logger.debug(f'ensure_connection() took {ensure_time:.2f}s')
            
            with connection.cursor() as cursor:
                query_start = time.time()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                query_time = time.time() - query_start
                health_logger.debug(f'Database query completed in {query_time:.2f}s')
                
                # Additional connection validation
                cursor.execute('SELECT version()')
                db_version = cursor.fetchone()[0]
                health_logger.debug(f'Database version: {db_version}')
                
                return True, None
        except OperationalError as e:
            error_context = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'connection_params': connection.get_connection_params(),
                'system_metrics': metrics,
                'db_metrics': db_metrics
            }
            health_logger.warning(
                'Initial database check failed. Context: %(context)s',
                {'context': json.dumps(error_context, indent=2)}
            )
            
            try:
                health_logger.debug('Closing existing connection...')
                connection.close()
                close_time = time.time()
                health_logger.debug('Establishing new connection...')
                connection.connect()
                connect_time = time.time() - close_time
                health_logger.debug(f'New connection established in {connect_time:.2f}s')
                
                with connection.cursor() as cursor:
                    retry_start = time.time()
                    cursor.execute('SELECT 1')
                    cursor.fetchone()
                    retry_time = time.time() - retry_start
                    health_logger.info(f'Database retry successful. Query time: {retry_time:.2f}s')
                    return True, None
            except Exception as retry_error:
                retry_context = {
                    'original_error': str(e),
                    'retry_error': str(retry_error),
                    'error_type': type(retry_error).__name__,
                    'connection_params': connection.get_connection_params(),
                    'system_metrics': metrics,
                    'db_metrics': db_metrics
                }
                error_msg = f"Database retry failed. Context: {json.dumps(retry_context, indent=2)}"
                health_logger.error(error_msg, exc_info=True)
                return False, error_msg
        except Exception as e:
            error_context = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'system_metrics': metrics,
                'db_metrics': db_metrics
            }
            error_msg = f"Database check failed. Context: {json.dumps(error_context, indent=2)}"
            health_logger.error(error_msg, exc_info=True)
            return False, error_msg

@never_cache
@require_GET
def health_check(request):
    """
    Health check endpoint for monitoring system status.
    Implements startup state handling and graceful database checks.
    """
    current_time = time.time()
    uptime = int(current_time - STARTUP_TIME)
    process_id = os.getpid()
    
    request_info = {
        'remote_addr': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'x_forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR'),
        'host': request.META.get('HTTP_HOST'),
        'method': request.method,
        'path': request.path,
    }
    
    health_logger.debug(
        'Health check request received. Context: %(context)s',
        {'context': json.dumps({
            'process_id': process_id,
            'uptime': uptime,
            'request': request_info
        }, indent=2)}
    )
    
    # During startup grace period, always return 200 OK
    if uptime < STARTUP_GRACE_PERIOD:
        health_logger.info(
            f'Health check during startup grace period '
            f'(uptime: {uptime}s, remaining: {STARTUP_GRACE_PERIOD - uptime}s)'
        )
        response_data = {
            'status': 'starting',
            'message': 'Application is starting up',
            'uptime': uptime,
            'grace_period_remaining': STARTUP_GRACE_PERIOD - uptime,
            'process_id': process_id,
            'timestamp': datetime.datetime.now().isoformat(),
            'system_metrics': get_system_metrics(),
            'hostname': socket.gethostname()
        }
        response = JsonResponse(response_data)
        response.status_code = 200
        return response
    
    # After grace period, check all systems
    start_time = time.time()
    
    # Check Redis first
    redis_healthy, redis_error = check_redis_connection()
    redis_check_time = time.time() - start_time
    
    # Then check database
    db_start_time = time.time()
    db_healthy, db_error = check_database()
    db_check_time = time.time() - db_start_time
    
    # Get system metrics
    system_metrics = get_system_metrics()
    
    total_check_duration = time.time() - start_time
    
    response_data = {
        'status': 'healthy' if (db_healthy and redis_healthy) else 'unhealthy',
        'uptime': uptime,
        'process_id': process_id,
        'check_duration': f'{total_check_duration:.2f}s',
        'checks': {
            'database': {
                'healthy': db_healthy,
                'duration': f'{db_check_time:.2f}s',
                'error': db_error if not db_healthy else None
            },
            'redis': {
                'healthy': redis_healthy,
                'duration': f'{redis_check_time:.2f}s',
                'error': redis_error if not redis_healthy else None
            }
        },
        'system_metrics': system_metrics,
        'timestamp': datetime.datetime.now().isoformat(),
        'hostname': socket.gethostname()
    }
    
    if not (db_healthy and redis_healthy):
        health_logger.error(
            'Health check failed. Context: %(context)s',
            {'context': json.dumps(response_data, indent=2)}
        )
        response = JsonResponse(response_data)
        response.status_code = 503
        return response
    
    health_logger.info(
        'Health check successful. Context: %(context)s',
        {'context': json.dumps({
            'duration': total_check_duration,
            'process_id': process_id,
            'system_metrics': system_metrics
        }, indent=2)}
    )
    response = JsonResponse(response_data)
    response.status_code = 200
    return response

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

class QuizListView(ListView):
    model = Quiz
    template_name = 'quiz/quiz_list.html'
    context_object_name = 'quizzes'
    paginate_by = 12  # Add pagination
    
    def get_queryset(self):
        """Optimize quiz list query with counts, caching, and pagination"""
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        cache_key = f'quiz_list_{user_id}'
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = Quiz.objects.filter(is_active=True).annotate(
                question_count=Count('questions'),
                total_attempts=Count('attempts', distinct=True),
                user_attempts=Count(
                    'attempts',
                    filter=Q(attempts__user_id=user_id),
                    distinct=True
                ) if user_id else Value(0),
                best_score=Coalesce(
                    Max('attempts__score', filter=Q(attempts__user_id=user_id)),
                    Value(0.0, output_field=FloatField())
                ) if user_id else Value(0.0, output_field=FloatField())
            ).prefetch_related(
                Prefetch('questions', queryset=Question.objects.only('id', 'text'))
            ).only(
                'id', 'title', 'description', 'image', 'created_at'
            ).order_by('-created_at')
            
            cache.set(cache_key, queryset, 300)  # Cache for 5 minutes
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_quizzes'] = Quiz.objects.filter(is_active=True).count()
        return context

class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'quiz/quiz_detail.html'
    
    def get_object(self, queryset=None):
        quiz_id = self.kwargs.get('pk')
        cache_key = f'quiz_detail_{quiz_id}'
        quiz = cache.get(cache_key)
        
        if quiz is None:
            quiz = super().get_object(queryset)
            cache.set(cache_key, quiz, 300)  # Cache for 5 minutes
            
        return quiz
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        
        if user_id:
            cache_key = f'quiz_detail_context_{self.object.id}_{user_id}'
            user_data = cache.get(cache_key)
            
            if user_data is None:
                user_data = {
                    'attempts': self.object.attempts.filter(user_id=user_id).count(),
                    'best_score': self.object.attempts.filter(user_id=user_id).aggregate(
                        best_score=Coalesce(Max('score'), Value(0))
                    )['best_score']
                }
                cache.set(cache_key, user_data, 300)  # Cache for 5 minutes
            
            context.update(user_data)
        
        return context

def clear_quiz_session(request):
    """Clear all quiz-related session data."""
    keys_to_remove = [
        'quiz_in_progress',
        'quiz_start_time',
        'current_question_index',
        'quiz_answers'
    ]
    for key in keys_to_remove:
        request.session.pop(key, None)
    request.session.modified = True

@login_required
@vary_on_cookie
def take_quiz(request, quiz_id):
    """Start or resume a quiz with optimized queries and caching."""
    cache_key = f'quiz_take_{quiz_id}'
    quiz = cache.get(cache_key)
    
    if quiz is None:
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related(
                Prefetch(
                    'questions',
                    queryset=Question.objects.prefetch_related(
                        Prefetch(
                            'choices',
                            queryset=Choice.objects.only('id', 'text', 'is_correct')
                        )
                    ).only('id', 'text', 'explanation', 'image')
                )
            ).only('id', 'title', 'description'),
            pk=quiz_id,
            is_active=True
        )
        cache.set(cache_key, quiz, 300)  # Cache for 5 minutes
    
    # Check for timeout first
    if 'quiz_start_time' in request.session:
        try:
            start_time = timezone.datetime.fromisoformat(str(request.session['quiz_start_time']))
            if timezone.now() - start_time > timedelta(minutes=60):
                clear_quiz_session(request)
                messages.warning(request, 'Quiz time limit exceeded.')
                return redirect('quiz:home')
        except (ValueError, TypeError):
            request.session['quiz_start_time'] = timezone.now().isoformat()
    
    # Check for existing quiz in progress
    if 'quiz_in_progress' in request.session:
        if request.session['quiz_in_progress'] != quiz_id:
            messages.warning(request, 'You have another quiz in progress.')
            return redirect('quiz:quiz_detail', pk=request.session['quiz_in_progress'])
    else:
        # Start new quiz
        request.session['quiz_start_time'] = timezone.now().isoformat()
        request.session['quiz_in_progress'] = quiz_id
        request.session['current_question_index'] = 0
        request.session['quiz_answers'] = {}
    
    # Get current question
    questions = list(quiz.questions.all())  # Already prefetched
    current_index = request.session.get('current_question_index', 0)
    
    if current_index >= len(questions):
        return redirect('quiz:quiz_results', quiz_id=quiz_id)
    
    current_question = questions[current_index]
    
    # Calculate time remaining
    start_time = timezone.datetime.fromisoformat(str(request.session['quiz_start_time']))
    elapsed_time = timezone.now() - start_time
    time_remaining = max(0, 60 - int(elapsed_time.total_seconds() / 60))
    
    context = {
        'quiz': quiz,
        'question': current_question,
        'time_remaining': time_remaining,
        'progress': {
            'current': current_index + 1,
            'total': len(questions),
            'percent': ((current_index + 1) / len(questions)) * 100
        }
    }
    
    return render(request, 'quiz/take_quiz.html', context)

@login_required
@transaction.atomic
def submit_quiz(request, quiz_id):
    """Submit and grade a quiz."""
    if request.method != 'POST':
        return redirect('quiz:take_quiz', quiz_id=quiz_id)
    
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related(
            Prefetch('questions', queryset=Question.objects.prefetch_related('choices'))
        ),
        pk=quiz_id
    )
    
    # Check for timeout
    if 'quiz_start_time' in request.session:
        try:
            start_time = timezone.datetime.fromisoformat(str(request.session['quiz_start_time']))
            if timezone.now() - start_time > timedelta(minutes=60):
                clear_quiz_session(request)
                messages.warning(request, 'Quiz time limit exceeded.')
                return redirect('quiz:home')
        except (ValueError, TypeError):
            clear_quiz_session(request)
            messages.error(request, 'Invalid session data.')
            return redirect('quiz:home')
    
    # Process answer
    questions = list(quiz.questions.all())  # Already prefetched
    current_index = request.session.get('current_question_index', 0)
    
    if current_index >= len(questions):
        messages.error(request, 'Invalid question index.')
        return redirect('quiz:home')
    
    current_question = questions[current_index]
    answer_key = f'question_{current_question.id}'
    answer = request.POST.get(answer_key)
    
    if not answer:
        messages.error(request, 'Please select an answer.')
        return redirect('quiz:take_quiz', quiz_id=quiz_id)
    
    # Store answer in session
    if 'quiz_answers' not in request.session:
        request.session['quiz_answers'] = {}
    
    request.session['quiz_answers'][str(current_index)] = answer
    request.session.modified = True
    
    # Move to next question or finish
    if current_index + 1 >= len(questions):
        # Calculate score
        score = 0
        for i, question in enumerate(questions):
            if str(i) in request.session['quiz_answers']:
                user_answer = request.session['quiz_answers'][str(i)]
                correct_answer = next(
                    (choice for choice in question.choices.all() if choice.is_correct),
                    None
                )
                if correct_answer and str(correct_answer.id) == str(user_answer):
                    score += 1
        
        # Store results
        results = {
            'score': (score / len(questions)) * 100,
            'total_questions': len(questions),
            'correct_answers': score,
            'passed': score >= (len(questions) * 0.8)  # 80% to pass
        }
        
        # Cache results
        cache_key = f'quiz_results_{quiz_id}_{request.user.id}'
        cache.set(cache_key, results, 3600)  # Cache for 1 hour
        
        request.session[f'quiz_{quiz_id}_results'] = results
        clear_quiz_session(request)
        
        return redirect('quiz:quiz_results', quiz_id=quiz_id)
    else:
        request.session['current_question_index'] = current_index + 1
        request.session.modified = True
        return redirect('quiz:take_quiz', quiz_id=quiz_id)

@login_required
@vary_on_cookie
@cache_page(300)  # Cache for 5 minutes
def quiz_results(request, quiz_id):
    """Display quiz results with optimized queries and caching."""
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related(
            Prefetch(
                'questions',
                queryset=Question.objects.prefetch_related(
                    Prefetch(
                        'choices',
                        queryset=Choice.objects.only('id', 'text', 'is_correct', 'explanation')
                    )
                ).only('id', 'text', 'explanation', 'image')
            )
        ).only('id', 'title', 'description'),
        pk=quiz_id,
        is_active=True
    )
    
    # Try to get results from cache first
    cache_key = f'quiz_results_{quiz_id}_{request.user.id}'
    results = cache.get(cache_key)
    
    if results is None:
        results = request.session.get(f'quiz_{quiz_id}_results', {
            'score': 0,
            'total_questions': quiz.questions.count(),
            'correct_answers': 0,
            'passed': False
        })
        
        # Cache user's quiz history
        user_history = QuizAttempt.objects.filter(
            quiz_id=quiz_id,
            user_id=request.user.id
        ).order_by('-created_at').values('score', 'created_at')[:5]
        
        results['history'] = list(user_history)
        cache.set(cache_key, results, 3600)  # Cache for 1 hour
    
    context = {
        'quiz': quiz,
        'score': results['score'],
        'total_questions': results['total_questions'],
        'correct_answers': results['correct_answers'],
        'passed': results['passed'],
        'history': results.get('history', [])
    }
    
    return render(request, 'quiz/quiz_results.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def handler403(request, exception):
    return render(request, '403.html', status=403)

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

@csrf_exempt
@require_POST
def log_client_error(request):
    """
    Endpoint for logging client-side errors.
    Accepts POST requests with JSON payload containing error details.
    """
    try:
        data = json.loads(request.body)
        logger = logging.getLogger('browser_errors')
        
        error_message = {
            'url': data.get('url', 'Unknown URL'),
            'message': data.get('message', 'No message provided'),
            'line': data.get('lineNo'),
            'column': data.get('columnNo'),
            'stack': data.get('error'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'referrer': request.META.get('HTTP_REFERER'),
        }
        
        logger.error(json.dumps(error_message))
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger = logging.getLogger('quiz')
        logger.error(f'Error logging client error: {str(e)}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@never_cache
def test_error_page(request):
    """
    A view to test different types of client-side errors.
    Includes examples of runtime errors, promise rejections, and network errors.
    """
    return render(request, 'quiz/test_errors.html')

def preview_page(request):
    """A simple view to test live preview functionality."""
    return render(request, 'quiz/preview.html')

def help_page(request):
    """View for the help page."""
    return render(request, 'quiz/help.html')
