"""
Login views using functional programming concepts.
"""
from typing import Dict, Optional, Tuple
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods
from django.conf import settings
from quiz.utils.functional_utils import (
    AuthResult, with_logging, validate_request, with_transaction,
    get_client_ip, check_login_attempts, increment_login_attempts,
    reset_login_attempts
)

import logging

logger = logging.getLogger(__name__)

def validate_login_data(data: Dict[str, str]) -> Tuple[bool, Optional[str]]:
    """Validate login form data."""
    if not data.get('username'):
        return False, 'Username/Email is required.'
    if not data.get('password'):
        return False, 'Password is required.'
    return True, None

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username/email and password."""
    # Try with username
    user = authenticate(username=username.lower(), password=password)
    if user:
        return user
    
    # Try with email
    try:
        user_obj = User.objects.get(email__iexact=username)
        user = authenticate(username=user_obj.username, password=password)
        if user:
            return user
    except User.DoesNotExist:
        pass
    
    return None

def handle_login(request: HttpRequest, data: Dict[str, str]) -> AuthResult:
    """Handle login in a functional way."""
    ip_address = get_client_ip(request)
    
    # Check login attempts
    is_allowed, error = check_login_attempts(ip_address)
    if not is_allowed:
        return AuthResult(
            success=False,
            message=settings.ACCOUNT_LOCKED_MESSAGE,
            template='quiz/auth/login.html'
        )
    
    # Validate data
    is_valid, error = validate_login_data(data)
    if not is_valid:
        return AuthResult(
            success=False,
            message=error,
            template='quiz/auth/login.html'
        )
    
    # Authenticate user
    user = authenticate_user(data['username'], data['password'])
    if not user:
        increment_login_attempts(ip_address)
        return AuthResult(
            success=False,
            message=settings.LOGIN_ERROR_MESSAGE,
            template='quiz/auth/login.html'
        )
    
    if not user.is_active:
        return AuthResult(
            success=False,
            message='Please verify your email address to activate your account.',
            template='quiz/auth/login.html'
        )
    
    # Login successful
    login(request, user)
    reset_login_attempts(ip_address)
    
    next_url = data.get('next')
    return AuthResult(
        success=True,
        message='Login successful.',
        redirect_to=next_url if next_url else 'quiz:dashboard'
    )

@sensitive_post_parameters()
@require_http_methods(['GET', 'POST'])
@validate_request
@with_logging(logger)
def login_view(request: HttpRequest) -> HttpResponse:
    """Handle user login using functional programming concepts."""
    if request.method == 'GET':
        return render(request, 'quiz/auth/login.html')

    result = with_transaction(lambda: handle_login(request, {
        'username': request.POST.get('username', ''),
        'password': request.POST.get('password', ''),
        'next': request.POST.get('next', '')
    }))()

    if result.message:
        messages.add_message(
            request,
            messages.SUCCESS if result.success else messages.ERROR,
            result.message
        )

    if result.redirect_to:
        return redirect(result.redirect_to)
    return render(request, result.template)
