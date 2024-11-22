"""
Email verification functionality using functional programming concepts.
"""
from typing import Dict, Optional, Tuple
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from quiz.utils.functional_utils import AuthResult, with_logging, validate_request, with_transaction
from quiz.settings.auth import (
    EMAIL_VERIFIED_MESSAGE,
    INVALID_VERIFICATION_LINK_MESSAGE
)

import logging

logger = logging.getLogger(__name__)

def validate_verification_request(request: HttpRequest, **kwargs) -> Tuple[bool, Optional[str]]:
    """Validate the verification request."""
    if request.method != 'GET':
        return False, 'Invalid request method.'
    
    uidb64 = kwargs.get('uidb64')
    token = kwargs.get('token')
    
    if not uidb64 or not token:
        return False, 'Invalid verification link.'
        
    return True, None

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
    try:
        token = generate_verification_token(user)
        uidb64 = encode_user_id(user)
        verification_url = request.build_absolute_uri(
            reverse('quiz:verify_email', kwargs={'uidb64': uidb64, 'token': token})
        )
        logger.info(f"Generated verification URL for user {user.username}: {verification_url}")
        return verification_url
    except Exception as e:
        logger.error(f"Error generating verification URL for user {user.username}: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def send_verification_email(request: HttpRequest, user: User) -> None:
    """Send verification email to the user."""
    try:
        verification_url = get_verification_url(request, user)
        subject = 'Verify your email address'
        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': settings.SITE_NAME,
            'support_email': settings.SUPPORT_EMAIL,
        }
        
        # Log the context for debugging
        logger.info(f"Preparing verification email for user {user.username}")
        
        # First try rendering the template
        try:
            message = render_to_string('quiz/auth/email/verification_email.html', context)
            logger.info(f"Successfully rendered email template for user {user.username}")
        except Exception as e:
            logger.error(f"Error rendering email template for user {user.username}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        
        # Create EmailMessage object for more control
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            reply_to=[settings.SUPPORT_EMAIL],
        )
        email.content_subtype = "html"  # Set content type to HTML
        
        # Log email settings
        logger.info(f"Email settings for user {user.username}: BACKEND={settings.EMAIL_BACKEND}, HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}")
        
        # Send the email
        email.send(fail_silently=False)
        logger.info(f"Verification email sent successfully to user {user.username}")
        
    except Exception as e:
        logger.error(f"Failed to send verification email to user {user.username}: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def verify_token(uidb64: str, token: str) -> AuthResult:
    """Verify the user's email verification token."""
    try:
        user_id = decode_user_id(uidb64)
        if not user_id:
            logger.warning(f"Invalid user ID in verification link: {uidb64}")
            return AuthResult(
                success=False,
                message=INVALID_VERIFICATION_LINK_MESSAGE,
                redirect_to='quiz:login'
            )

        try:
            user = User.objects.get(pk=user_id)
            logger.info(f"Found user {user.username} for verification")
        except User.DoesNotExist:
            logger.warning(f"No user found for ID {user_id} during verification")
            return AuthResult(
                success=False,
                message=INVALID_VERIFICATION_LINK_MESSAGE,
                redirect_to='quiz:login'
            )

        if user.is_active:
            logger.info(f"User {user.username} is already verified")
            return AuthResult(
                success=True,
                message="Your account is already verified. Please login.",
                redirect_to='quiz:login'
            )

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            logger.info(f"Successfully verified user {user.username}")
            return AuthResult(
                success=True,
                message=EMAIL_VERIFIED_MESSAGE,
                redirect_to='quiz:login'
            )
        else:
            logger.warning(f"Invalid token for user {user.username} during verification")
            return AuthResult(
                success=False,
                message=INVALID_VERIFICATION_LINK_MESSAGE,
                redirect_to='quiz:login'
            )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        logger.error(traceback.format_exc())
        return AuthResult(
            success=False,
            message=INVALID_VERIFICATION_LINK_MESSAGE,
            redirect_to='quiz:login'
        )

@require_http_methods(['GET'])
def verify_email_view(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """Handle email verification."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        logger.warning(f"Invalid verification link: uidb64={uidb64}")
        messages.error(request, "Invalid verification link.")
        return redirect('quiz:login')
    
    # Check if user is already verified
    if user.is_active:
        logger.info(f"User {user.email} is already verified")
        messages.info(request, "Your email is already verified. You can login.")
        return redirect('quiz:login')
    
    # Verify token
    if not default_token_generator.check_token(user, token):
        logger.warning(f"Invalid/expired token for user {user.email}")
        messages.error(request, "Verification link has expired.")
        return redirect('quiz:login')
    
    # Activate user
    try:
        user.is_active = True
        user.save()
        logger.info(f"User {user.email} verified successfully")
        messages.success(request, "Your email has been verified. You can now login.")
        return redirect('quiz:login')
    except Exception as e:
        logger.error(f"Error activating user {user.email}: {str(e)}")
        messages.error(request, "Failed to verify email. Please try again.")
        return redirect('quiz:login')

@require_http_methods(['GET', 'POST'])
def resend_verification(request: HttpRequest) -> HttpResponse:
    """Handle resending verification email."""
    if request.method == 'GET':
        return render(request, 'quiz/auth/resend_verification.html')
    
    email = request.POST.get('email', '')
    if not email:
        messages.error(request, "Please enter your email address.")
        return render(request, 'quiz/auth/resend_verification.html', status=400)
    
    try:
        user = User.objects.get(email=email)
        
        # Check if user is already verified
        if user.is_active:
            messages.info(request, "Your email is already verified. You can login.")
            return redirect('quiz:login')
        
        # Resend verification email
        send_verification_email(request, user)
        messages.success(request, "Verification email has been resent. Please check your inbox.")
        return redirect('quiz:login')
        
    except User.DoesNotExist:
        messages.error(request, "No account found with this email address.")
        return render(request, 'quiz/auth/resend_verification.html', status=400)
    except Exception as e:
        logger.error(f"Error resending verification email: {str(e)}")
        messages.error(request, "Failed to resend verification email. Please try again later.")
        return render(request, 'quiz/auth/resend_verification.html', status=500)
