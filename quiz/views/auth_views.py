"""
Views for handling user authentication.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.conf import settings
from ..forms import CustomUserCreationForm
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Constants
LOGIN_ATTEMPTS_TIMEOUT = getattr(settings, 'LOGIN_ATTEMPTS_TIMEOUT', 300)  # 5 minutes
MAX_LOGIN_ATTEMPTS = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
User = get_user_model()


def get_client_ip(request) -> str:
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def check_login_attempts(ip_address: str) -> bool:
    """Check if IP has exceeded maximum login attempts."""
    cache_key = f'login_attempts_{ip_address}'
    attempts = cache.get(cache_key, 0)
    return attempts >= MAX_LOGIN_ATTEMPTS


def increment_login_attempts(ip_address: str) -> None:
    """Increment login attempts for IP address."""
    cache_key = f'login_attempts_{ip_address}'
    attempts = cache.get(cache_key, 0)
    cache.set(cache_key, attempts + 1, LOGIN_ATTEMPTS_TIMEOUT)


def reset_login_attempts(ip_address: str) -> None:
    """Reset login attempts for IP address."""
    cache_key = f'login_attempts_{ip_address}'
    cache.delete(cache_key)


@sensitive_post_parameters('password1', 'password2')
@csrf_protect
@never_cache
@require_http_methods(["GET", "POST"])
def register(request):
    """Handle user registration with enhanced security and validation."""
    if request.user.is_authenticated:
        messages.info(request, 'You are already registered and logged in.')
        return redirect('quiz:quiz_list')
    
    ip_address = get_client_ip(request)
    if check_login_attempts(ip_address):
        messages.error(
            request,
            f'Too many registration attempts. Please try again in {LOGIN_ATTEMPTS_TIMEOUT // 60} minutes.'
        )
        return render(request, 'registration/register.html', {'form': None}, status=429)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                # Add additional user setup if needed
                user.save()
                
                # Log the user in
                login(request, user)
                
                # Reset login attempts on successful registration
                reset_login_attempts(ip_address)
                
                messages.success(
                    request,
                    'Registration successful! Welcome to our quiz platform.'
                )
                logger.info(f'New user registered: {user.username}')
                
                return redirect('quiz:quiz_list')
            
            except Exception as e:
                logger.error(f'Registration failed for {form.cleaned_data.get("username")}: {str(e)}')
                messages.error(
                    request,
                    'Registration failed. Please try again or contact support.'
                )
        else:
            increment_login_attempts(ip_address)
            logger.warning(
                f'Failed registration attempt from IP: {ip_address}'
            )
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'page_title': 'Register',
        'social_login': getattr(settings, 'SOCIAL_AUTH_PROVIDERS', {}),
        'password_requirements': {
            'min_length': settings.AUTH_PASSWORD_VALIDATORS[0].get('OPTIONS', {}).get('min_length', 8),
            'special_chars': True,
            'numbers': True,
            'uppercase': True
        }
    }
    
    response = render(request, 'registration/register.html', context)
    response['X-Frame-Options'] = 'DENY'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response


from django.contrib.auth.decorators import login_required

@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')
