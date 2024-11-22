"""
Email verification functionality using functional programming concepts.
"""
from typing import Dict, Optional
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from ..functional_utils import AuthResult, with_logging, validate_request
from ..decorators import with_transaction

import logging

logger = logging.getLogger(__name__)

def generate_verification_token(user: User) -> str:
    """Generate a verification token for the user."""
    return default_token_generator.make_token(user)

def encode_user_id(user: User) -> str:
    """Encode user ID for verification URL."""
    return urlsafe_base64_encode(force_bytes(user.pk))

def decode_user_id(uidb64: str) -> Optional[int]:
    """Decode user ID from verification URL."""
    try:
        return int(force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError):
        return None

def get_verification_url(request: HttpRequest, user: User) -> str:
    """Generate the complete verification URL."""
    token = generate_verification_token(user)
    uidb64 = encode_user_id(user)
    return request.build_absolute_uri(
        reverse('quiz:verify_email', kwargs={'uidb64': uidb64, 'token': token})
    )

def send_verification_email(request: HttpRequest, user: User) -> None:
    """Send verification email to the user."""
    verification_url = get_verification_url(request, user)
    subject = 'Verify your email address'
    message = render_to_string('quiz/auth/email/verification_email.html', {
        'user': user,
        'verification_url': verification_url,
        'site_name': settings.SITE_NAME,
    })
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )

def verify_token(uidb64: str, token: str) -> AuthResult:
    """Verify the user's email verification token."""
    user_id = decode_user_id(uidb64)
    if not user_id:
        return AuthResult(
            success=False,
            message='Invalid verification link.',
            redirect_to='quiz:login'
        )

    try:
        user = User.objects.get(pk=user_id)
        if default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save()
                return AuthResult(
                    success=True,
                    message='Email verified successfully. You can now log in.',
                    redirect_to='quiz:login'
                )
            return AuthResult(
                success=True,
                message='Email already verified.',
                redirect_to='quiz:login'
            )
        return AuthResult(
            success=False,
            message='Invalid verification link.',
            redirect_to='quiz:login'
        )
    except User.DoesNotExist:
        return AuthResult(
            success=False,
            message='Invalid verification link.',
            redirect_to='quiz:login'
        )

@validate_request
@with_logging(logger)
def verify_email_view(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """Handle email verification."""
    result = with_transaction(lambda: verify_token(uidb64, token))()
    
    if result.message:
        messages.add_message(
            request,
            messages.SUCCESS if result.success else messages.ERROR,
            result.message
        )
    
    return redirect(result.redirect_to)
