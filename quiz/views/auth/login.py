"""
Login views using functional programming concepts.
"""
from typing import Dict, Optional, Tuple
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.urls import reverse
from quiz.utils.functional_utils import (
    get_client_ip, check_login_attempts, increment_login_attempts,
    reset_login_attempts
)
from quiz.settings.auth import (
    LOGIN_ERROR_MESSAGE,
    EMAIL_VERIFICATION_REQUIRED_MESSAGE,
    ACCOUNT_LOCKED_MESSAGE,
)

import logging

logger = logging.getLogger(__name__)

@sensitive_post_parameters('password')
@require_http_methods(['GET', 'POST'])
def login_view(request: HttpRequest) -> HttpResponse:
    """Handle user login."""
    # Get the next URL if provided
    next_url = request.GET.get('next', reverse('quiz:dashboard'))
    
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'quiz/auth/login.html', {
            'form': form,
            'next': next_url
        }, status=200)
    
    # Get client IP
    ip_address = get_client_ip(request)
    
    # Check if account is locked
    if check_login_attempts(ip_address):
        logger.warning(f"Account locked for IP {ip_address} due to too many failed attempts")
        messages.error(request, ACCOUNT_LOCKED_MESSAGE)
        form = AuthenticationForm()
        return render(request, 'quiz/auth/login.html', {
            'form': form,
            'account_locked': True,
            'next': next_url
        }, status=403)
    
    # Process login form
    form = AuthenticationForm(request, data=request.POST)
    if not form.is_valid():
        # Log failed attempt
        increment_login_attempts(ip_address)
        messages.error(request, LOGIN_ERROR_MESSAGE)
        
        # Check if rate limit exceeded after increment
        if check_login_attempts(ip_address):
            messages.error(request, ACCOUNT_LOCKED_MESSAGE)
            return render(request, 'quiz/auth/login.html', {
                'form': form,
                'account_locked': True,
                'next': next_url
            }, status=403)
        return render(request, 'quiz/auth/login.html', {
            'form': form,
            'next': next_url
        }, status=401)
    
    # Get the user from the form
    user = form.get_user()
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user {user.username}")
        messages.warning(request, EMAIL_VERIFICATION_REQUIRED_MESSAGE)
        return render(request, 'quiz/auth/login.html', {
            'form': form,
            'email_unverified': True,
            'next': next_url
        }, status=403)
    
    # Login successful
    login(request, user)
    reset_login_attempts(ip_address)
    logger.info(f"User {user.username} logged in successfully")
    messages.success(request, f"Welcome back, {user.username}!")
    
    # Validate next URL
    if not next_url.startswith('/'):
        next_url = reverse('quiz:dashboard')
    
    # Redirect to success URL
    response = redirect(next_url)
    response.status_code = 302  # Explicit redirect status
    return response
