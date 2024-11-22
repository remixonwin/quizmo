"""
Registration views using functional programming concepts.
"""
from typing import Dict, Optional, Tuple
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods
from django.conf import settings
from quiz.utils.functional_utils import AuthResult, with_logging, validate_request, with_transaction
from .verification import send_verification_email

import logging

logger = logging.getLogger(__name__)

def validate_registration_data(data: Dict[str, str]) -> Tuple[bool, Optional[str]]:
    """Validate registration form data."""
    required_fields = ['username', 'email', 'password1', 'password2']
    
    # Check required fields
    for field in required_fields:
        if not data.get(field):
            return False, f'{field.title()} is required.'
    
    # Check passwords match
    if data['password1'] != data['password2']:
        return False, 'Passwords do not match.'
    
    # Validate password
    try:
        validate_password(data['password1'])
    except ValidationError as e:
        return False, ' '.join(e.messages)
    
    # Check email domain
    email_domain = data['email'].split('@')[1]
    if email_domain in settings.BLACKLISTED_EMAIL_DOMAINS:
        return False, f'Email domain {email_domain} is not allowed.'
    
    return True, None

def create_user(data: Dict[str, str]) -> User:
    """Create a new user with the given data."""
    username = data['username'].lower()
    email = data['email'].lower()
    
    # Check if username exists
    if User.objects.filter(username__iexact=username).exists():
        raise ValidationError('Username already exists.')
    
    # Check if email exists
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError('Email already registered.')
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=data['password1'],
        is_active=False  # User needs to verify email
    )
    
    return user

def handle_registration(request: HttpRequest, data: Dict[str, str]) -> AuthResult:
    """Handle registration in a functional way."""
    try:
        # Validate data
        is_valid, error = validate_registration_data(data)
        if not is_valid:
            return AuthResult(
                success=False,
                message=error,
                template='quiz/auth/register.html'
            )
        
        # Create user
        user = create_user(data)
        
        # Send verification email
        send_verification_email(request, user)
        
        return AuthResult(
            success=True,
            message=settings.REGISTRATION_SUCCESS_MESSAGE,
            redirect_to='quiz:login',
            template='quiz/auth/register.html'
        )
    
    except ValidationError as e:
        return AuthResult(
            success=False,
            message=str(e),
            template='quiz/auth/register.html'
        )
    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
        return AuthResult(
            success=False,
            message='Registration failed. Please try again.',
            template='quiz/auth/register.html'
        )

@sensitive_post_parameters()
@require_http_methods(['GET', 'POST'])
@validate_request
@with_logging(logger)
def register_view(request: HttpRequest) -> HttpResponse:
    """Handle user registration using functional programming concepts."""
    if request.method == 'GET':
        return render(request, 'quiz/auth/register.html')

    result = with_transaction(lambda: handle_registration(request, {
        'username': request.POST.get('username', ''),
        'email': request.POST.get('email', ''),
        'password1': request.POST.get('password1', ''),
        'password2': request.POST.get('password2', ''),
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
