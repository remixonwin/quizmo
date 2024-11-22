"""
Views for handling user authentication.
"""
import logging
import re
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Q, Count, Avg, FloatField, Case, When, Value, F
from django.utils.html import strip_tags

from ..forms import CustomUserCreationForm
from ..settings.auth import (
    MAX_LOGIN_ATTEMPTS,
    LOGIN_ATTEMPTS_TIMEOUT,
    ACCOUNT_LOCKOUT_DURATION,
    EMAIL_VERIFICATION_REQUIRED,
    EMAIL_VERIFICATION_REQUIRED_MESSAGE,
    LOGIN_ERROR_MESSAGE,
    ACCOUNT_LOCKED_MESSAGE,
    INVALID_TOKEN_MESSAGE,
    BLACKLISTED_EMAIL_DOMAINS,
    EMAIL_NOT_REGISTERED_MESSAGE,
    REGISTRATION_SUCCESS_MESSAGE,
    PASSWORD_RESET_SENT_MESSAGE,
    PASSWORD_RESET_SUCCESS_MESSAGE,
    PASSWORD_RESET_INVALID_TOKEN_MESSAGE,
    PASSWORD_RESET_TIMEOUT,
)
from ..utils.security import get_client_ip
from ..utils.logging import security_logger, auth_logger
from ..utils.tokens import email_verification_token_generator as email_verification_token
from ..models import QuizAttempt, Quiz

logger = logging.getLogger(__name__)

def check_login_attempts(ip_address):
    """Check if the IP has exceeded the maximum login attempts."""
    attempts = cache.get(f'login_attempts_{ip_address}', 0)
    if attempts >= MAX_LOGIN_ATTEMPTS:
        # Check if the account is still in lockout period
        last_attempt = cache.get(f'last_attempt_{ip_address}')
        if last_attempt and (timezone.now() - last_attempt).seconds < ACCOUNT_LOCKOUT_DURATION:
            return True
        # Reset if lockout period has passed
        reset_login_attempts(ip_address)
        return False
    return False

def increment_login_attempts(ip_address):
    """Increment the number of login attempts for an IP."""
    attempts = cache.get(f'login_attempts_{ip_address}', 0)
    cache.set(f'login_attempts_{ip_address}', attempts + 1, LOGIN_ATTEMPTS_TIMEOUT)
    if attempts + 1 >= MAX_LOGIN_ATTEMPTS:
        cache.set(f'last_attempt_{ip_address}', timezone.now(), ACCOUNT_LOCKOUT_DURATION)
        security_logger.warning(f'Failed login attempt from IP: {ip_address}. Attempts: {attempts + 1}')
        return True
    security_logger.warning(f'Failed login attempt from IP: {ip_address}. Attempts: {attempts + 1}')
    return False

def reset_login_attempts(ip_address):
    """Reset login attempts for an IP."""
    cache.delete(f'login_attempts_{ip_address}')
    cache.delete(f'last_attempt_{ip_address}')

def check_reset_attempts(ip_address):
    """Check if the IP has exceeded the maximum password reset attempts."""
    attempts = cache.get(f'reset_attempts_{ip_address}', 0)
    if attempts >= 5:  # Max 5 attempts
        # Check if still in timeout period (15 minutes)
        last_attempt = cache.get(f'last_reset_attempt_{ip_address}')
        if last_attempt and (timezone.now() - last_attempt).seconds < 900:  # 15 minutes
            return True
        # Reset if timeout period has passed
        reset_reset_attempts(ip_address)
        return False
    return False

def increment_reset_attempts(ip_address):
    """Increment the number of password reset attempts for an IP."""
    attempts = cache.get(f'reset_attempts_{ip_address}', 0)
    cache.set(f'reset_attempts_{ip_address}', attempts + 1, 3600)  # 1 hour timeout
    if attempts + 1 >= 5:
        cache.set(f'last_reset_attempt_{ip_address}', timezone.now(), 900)  # 15 minutes lockout
        security_logger.warning(f'Password reset rate limit exceeded for IP: {ip_address}')
        return True
    return False

def reset_reset_attempts(ip_address):
    """Reset password reset attempts for an IP."""
    cache.delete(f'reset_attempts_{ip_address}')
    cache.delete(f'last_reset_attempt_{ip_address}')

@sensitive_post_parameters()
@never_cache
@require_http_methods(['GET', 'POST'])
def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('quiz:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        ip_address = get_client_ip(request)

        # Check login attempts
        if check_login_attempts(ip_address):
            messages.error(request, ACCOUNT_LOCKED_MESSAGE)
            security_logger.warning(f'Blocked login attempt from locked IP: {ip_address}')
            response = render(request, 'quiz/auth/login.html')
            response.status_code = 429  # Too Many Requests
            return response

        # Try to authenticate with case-insensitive username
        try:
            user_obj = User.objects.filter(username__iexact=username).first()
            if not user_obj:
                # If no username match, try with email
                user_obj = User.objects.filter(email__iexact=username).first()

            if user_obj:
                if not user_obj.is_active:
                    messages.error(request, EMAIL_VERIFICATION_REQUIRED_MESSAGE)
                    auth_logger.warning(f'Inactive user login attempt: {user_obj.username}')
                    return render(request, 'quiz/auth/login.html')
                
                user = authenticate(username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    reset_login_attempts(ip_address)
                    auth_logger.info(f'Successful login for user: {user.username}')
                    messages.success(request, f'Welcome back, {user.username}!')
                    
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('quiz:dashboard')
            else:
                user = None
                messages.error(request, LOGIN_ERROR_MESSAGE)
                auth_logger.warning(f'Failed login attempt for username: {username}')
        except Exception as e:
            security_logger.error(f'Authentication error: {str(e)}')
            user = None
            messages.error(request, LOGIN_ERROR_MESSAGE)

        # Handle failed login
        if increment_login_attempts(ip_address):
            messages.error(request, ACCOUNT_LOCKED_MESSAGE)
            response = render(request, 'quiz/auth/login.html')
            response.status_code = 429  # Too Many Requests
            return response

    return render(request, 'quiz/auth/login.html')

@sensitive_post_parameters()
@never_cache
@require_http_methods(['GET', 'POST'])
def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('quiz:dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = None
            try:
                # Create inactive user
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                # Send verification email
                send_verification_email(request, user)
                messages.success(request, REGISTRATION_SUCCESS_MESSAGE)
                return redirect('quiz:login')
            except Exception as e:
                logger.error(f'Failed to send verification email: {str(e)}')
                if user and user.pk:
                    user.delete()
                messages.error(request, 'Failed to send verification email. Please try again.')
        return render(request, 'quiz/auth/register.html', {'form': form})

    form = CustomUserCreationForm()
    return render(request, 'quiz/auth/register.html', {'form': form})

def send_verification_email(request, user):
    """Send verification email to user."""
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_url = request.build_absolute_uri(
        reverse('quiz:verify_email', args=[uid, token])
    )

    subject = 'Verify your QuizApp email'
    html_message = render_to_string('quiz/auth/email_verification.html', {
        'user': user,
        'verification_url': verification_url,
        'protocol': 'https' if request.is_secure() else 'http',
        'domain': request.get_host(),
    })
    
    send_mail(
        subject,
        'Please verify your email address to complete registration.',
        'noreply@quizapp.com',
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

@require_http_methods(['GET'])
def verify_email(request, uidb64, token):
    """Verify user's email address."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email verification successful! You can now login.')
        return redirect('quiz:login')
    else:
        messages.error(request, 'Invalid verification link. Please try again.')
        response = render(request, 'quiz/auth/register.html')
        response.status_code = 400
        return response

@sensitive_post_parameters()
@never_cache
@require_http_methods(['GET', 'POST'])
def password_reset_view(request):
    """Handle password reset request."""
    if request.method == 'POST':
        ip_address = get_client_ip(request)
        
        # Check rate limiting
        if check_reset_attempts(ip_address):
            messages.error(request, 'Too many requests. Please try again later.')
            response = render(request, 'quiz/auth/password_reset.html')
            response.status_code = 429  # Too Many Requests
            return response
            
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.error(request, EMAIL_VERIFICATION_REQUIRED_MESSAGE)
                return render(request, 'quiz/auth/password_reset.html')
        except User.DoesNotExist:
            messages.error(request, EMAIL_NOT_REGISTERED_MESSAGE)
            auth_logger.warning(f'Password reset attempt for non-existent email: {email}')
            return render(request, 'quiz/auth/password_reset.html')

        # Generate token with timeout
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build reset URL
        reset_url = request.build_absolute_uri(
            reverse('quiz:password_reset_confirm', args=[uid, token])
        )

        # Send email
        subject_template = 'quiz/auth/password_reset_subject.txt'
        email_template = 'quiz/auth/password_reset_email.html'
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'support_email': 'support@quizapp.com',
            'timeout_hours': PASSWORD_RESET_TIMEOUT // 3600,
            'site_name': 'QuizApp',
        }
        
        try:
            subject = render_to_string(subject_template).strip()
            html_message = render_to_string(email_template, context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                'noreply@quizapp.com',
                [email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Increment attempts only on successful email send
            if increment_reset_attempts(ip_address):
                messages.warning(request, 'Maximum reset attempts reached. Please try again later.')
            else:
                messages.success(request, PASSWORD_RESET_SENT_MESSAGE)
                
            auth_logger.info(f'Password reset email sent to {email}')
            return redirect('quiz:login')
            
        except Exception as e:
            logger.error(f'Failed to send password reset email to {email}: {str(e)}')
            messages.error(request, 'Failed to send password reset email. Please try again.')
            return render(request, 'quiz/auth/password_reset.html')

    return render(request, 'quiz/auth/password_reset.html')

@sensitive_post_parameters()
@never_cache
@require_http_methods(['GET', 'POST'])
def password_reset_confirm_view(request, uidb64, token):
    """Handle password reset confirmation."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not user.is_active:
            messages.error(request, EMAIL_VERIFICATION_REQUIRED_MESSAGE)
            return render(request, 'quiz/auth/password_reset.html')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        auth_logger.warning(f'Invalid password reset attempt with uidb64: {uidb64}')

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')

            if not password1 or not password2:
                messages.error(request, 'Please enter both passwords')
                return render(request, 'quiz/auth/password_reset_confirm.html', {'validlink': True})

            if password1 != password2:
                messages.error(request, 'Passwords do not match')
                return render(request, 'quiz/auth/password_reset_confirm.html', {'validlink': True})

            try:
                # Validate password strength
                validate_password(password1, user)
                
                # Set new password and clear any session data
                user.set_password(password1)
                user.save()
                
                # Clear any existing sessions for this user
                from django.contrib.sessions.models import Session
                Session.objects.filter(expire_date__gte=timezone.now()).filter(
                    session_data__contains=str(user.id)
                ).delete()
                
                messages.success(request, PASSWORD_RESET_SUCCESS_MESSAGE)
                auth_logger.info(f'Password reset successful for user {user.username}')
                return redirect('quiz:login')
                
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return render(request, 'quiz/auth/password_reset_confirm.html', {'validlink': True})
        return render(request, 'quiz/auth/password_reset_confirm.html', {'validlink': True})
    else:
        messages.error(request, PASSWORD_RESET_INVALID_TOKEN_MESSAGE)
        auth_logger.warning(f'Invalid password reset token for uidb64: {uidb64}')
        response = render(request, 'quiz/auth/password_reset.html')
        response.status_code = 400
        return response

@require_http_methods(['GET'])
def logout_view(request):
    """Handle user logout."""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('quiz:login')

@login_required
@require_http_methods(['GET'])
def profile(request):
    """Display and update user profile and quiz statistics."""
    # Get user's quiz attempts
    quiz_attempts = QuizAttempt.objects.filter(user=request.user)
    
    # Calculate quiz statistics
    quiz_stats = quiz_attempts.aggregate(
        total_attempts=Count('id'),
        total_completed=Count('id', filter=Q(completed_at__isnull=False)),
        avg_score=Avg(
            Case(
                When(completed_at__isnull=False, then='score'),
                default=0,
                output_field=FloatField(),
            )
        )
    )

    # Format statistics for display
    stats = {
        'total_attempts': quiz_stats['total_attempts'],
        'total_completed': quiz_stats['total_completed'],
        'avg_score': f"{quiz_stats['avg_score']:.1f}%" if quiz_stats['avg_score'] is not None else "0.0%",
        'completion_rate': f"{(quiz_stats['total_completed'] / quiz_stats['total_attempts'] * 100):.1f}%" 
            if quiz_stats['total_attempts'] > 0 else "0.0%"
    }

    context = {
        'user': request.user,
        'stats': stats,
        'recent_attempts': quiz_attempts.order_by('-started_at')[:5]
    }

    return render(request, 'quiz/auth/profile.html', context)

@login_required
@require_http_methods(['GET'])
def dashboard(request):
    """Display user dashboard with quiz statistics."""
    user = request.user
    ip_address = get_client_ip(request)
    auth_logger.info(f'Dashboard accessed by user: {user.username} from IP: {ip_address}')
    
    # Get recent quiz attempts
    recent_attempts = QuizAttempt.objects.filter(
        user=request.user
    ).select_related('quiz').order_by('-created_at')[:5]

    # Get user's quiz statistics
    quiz_stats = QuizAttempt.objects.filter(user=request.user).aggregate(
        total_attempts=Count('id'),
        avg_score=Avg('score', output_field=FloatField()),
        passed_quizzes=Count('id', filter=Q(score__gte=F('quiz__passing_score'))),
        perfect_scores=Count(Case(When(score=100, then=Value(1))))
    )

    # Get available quizzes
    available_quizzes = Quiz.objects.filter(
        is_active=True
    ).exclude(
        id__in=QuizAttempt.objects.filter(
            user=request.user,
            score__gte=F('quiz__passing_score')
        ).values('quiz_id')
    ).order_by('title')[:5]

    context = {
        'user': user,
        'recent_attempts': recent_attempts,
        'quiz_stats': quiz_stats,
        'available_quizzes': available_quizzes,
    }
    return render(request, 'quiz/dashboard.html', context)

@require_http_methods(['GET'])
def privacy_policy(request):
    """Display privacy policy page."""
    return render(request, 'quiz/privacy_policy.html')
