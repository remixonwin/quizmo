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
from django.core.validators import validate_email
from quiz.utils.functional_utils import AuthResult, with_logging, validate_request, with_transaction
from quiz.forms import CustomUserCreationForm
from quiz.settings.auth import (
    REGISTRATION_SUCCESS_MESSAGE,
    PASSWORD_MISMATCH_MESSAGE,
    PASSWORD_COMPLEXITY_MESSAGE,
    EMAIL_DOMAIN_ERROR_MESSAGE,
    EMAIL_EXISTS_MESSAGE,
    USERNAME_EXISTS_MESSAGE
)
from .verification import send_verification_email

import logging

logger = logging.getLogger(__name__)

def validate_request_data(request: HttpRequest) -> Tuple[bool, Optional[str]]:
    """Validate the request data."""
    if request.method == 'GET':
        return True, None
        
    if request.method != 'POST':
        return False, 'Invalid request method.'
        
    return True, None

def validate_password_complexity(password: str) -> None:
    """Validate password complexity requirements."""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters')
    if not any(c.isupper() for c in password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not any(c.isdigit() for c in password):
        raise ValidationError('Password must contain at least one number')

def handle_registration(request: HttpRequest, form: CustomUserCreationForm) -> AuthResult:
    """Handle registration in a functional way."""
    try:
        if not form.is_valid():
            # Add specific error messages for password validation
            if 'password1' in form.errors:
                try:
                    validate_password_complexity(form.cleaned_data.get('password1', ''))
                except ValidationError as e:
                    for error in e.messages:
                        messages.error(request, error)
                        form.add_error('password1', error)
            
            # Add specific error messages for email validation
            if 'email' in form.errors:
                email = form.cleaned_data.get('email', '')
                try:
                    validate_email(email)
                    if User.objects.filter(email__iexact=email).exists():
                        messages.error(request, EMAIL_EXISTS_MESSAGE)
                    else:
                        domain = email.split('@')[1] if '@' in email else ''
                        if domain.lower() in ['example.com', 'test.com']:
                            messages.error(request, EMAIL_DOMAIN_ERROR_MESSAGE)
                except ValidationError:
                    messages.error(request, 'Please enter a valid email address.')
            
            # Add specific error message for username
            if 'username' in form.errors:
                username = form.cleaned_data.get('username', '')
                if User.objects.filter(username__iexact=username).exists():
                    messages.error(request, USERNAME_EXISTS_MESSAGE)
            
            # Add specific error message for password mismatch
            if 'password2' in form.errors:
                messages.error(request, PASSWORD_MISMATCH_MESSAGE)
            
            return AuthResult(
                success=False,
                message="Please correct the errors below.",
                template='quiz/auth/register.html',
                data={'form': form},
                status_code=400  # Return 400 for form validation errors
            )
        
        # Create user
        user = form.save(commit=False)
        user.is_active = False  # User needs to verify email
        user.save()
        
        # Send verification email
        send_verification_email(request, user)
        
        messages.success(request, REGISTRATION_SUCCESS_MESSAGE)
        return AuthResult(
            success=True,
            message=REGISTRATION_SUCCESS_MESSAGE,
            redirect_to='quiz:login',
            status_code=302  # HTTP_FOUND for redirect
        )
    
    except ValidationError as e:
        if 'domain' in str(e).lower():
            messages.error(request, EMAIL_DOMAIN_ERROR_MESSAGE)
        elif 'email' in str(e).lower():
            messages.error(request, 'Please enter a valid email address.')
        else:
            messages.error(request, str(e))
        
        return AuthResult(
            success=False,
            message=str(e),
            template='quiz/auth/register.html',
            data={'form': form},
            status_code=400  # Return 400 for validation errors
        )
    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
        messages.error(request, 'Registration failed. Please try again.')
        return AuthResult(
            success=False,
            message='Registration failed. Please try again.',
            template='quiz/auth/register.html',
            data={'form': form},
            status_code=500  # Return 500 for server errors
        )

@sensitive_post_parameters()
@require_http_methods(['GET', 'POST'])
@validate_request(validate_request_data)
@with_logging(logger)
def register_view(request: HttpRequest) -> HttpResponse:
    """Handle user registration using functional programming concepts."""
    if request.method == 'GET':
        form = CustomUserCreationForm()
        return render(request, 'quiz/auth/register.html', {'form': form}, status=200)

    form = CustomUserCreationForm(request.POST)
    
    # Get the result from the transaction
    result = with_transaction(lambda: handle_registration(request, form))
    
    # Execute the transaction function
    result = result()
    
    # Handle the result
    if result.redirect_to:
        response = redirect(result.redirect_to)
        response.status_code = result.status_code or 302
        return response
    
    return render(request, result.template, result.data or {'form': form}, status=result.status_code or 400)
