"""
Token utilities for the quiz app.
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
import base64
import hashlib

def generate_token(user, purpose='default', expiry=3600):
    """Generate a secure token for a user with a specific purpose."""
    signer = TimestampSigner()
    data = f'{user.pk}:{purpose}:{get_random_string(32)}'
    return signer.sign_object(data)

def verify_token(token, user=None, purpose='default', max_age=3600):
    """Verify a token and return True if valid."""
    try:
        signer = TimestampSigner()
        data = signer.unsign_object(token, max_age=max_age)
        if not isinstance(data, str):
            return False
            
        user_id, token_purpose, _ = data.split(':', 2)
        
        if purpose != token_purpose:
            return False
            
        if user and str(user.pk) != user_id:
            return False
            
        return True
    except (BadSignature, SignatureExpired, ValueError):
        return False

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for email verification."""
    def _make_hash_value(self, user, timestamp):
        """Create a unique hash value for email verification."""
        login_timestamp = (
            ''
            if user.last_login is None
            else user.last_login.replace(microsecond=0, tzinfo=None).isoformat()
        )
        email_field = user.get_email_field_name()
        email = getattr(user, email_field, '') or ''
        return f'{user.pk}{user.password}{login_timestamp}{timestamp}{email}{user.is_active}'

email_verification_token_generator = EmailVerificationTokenGenerator()

def generate_email_token(user):
    """Generate a token for email verification."""
    return email_verification_token_generator.make_token(user)

def verify_email_token(user, token):
    """Verify an email verification token."""
    return email_verification_token_generator.check_token(user, token)

def encode_user_id(user_id):
    """Encode a user ID for use in verification URLs."""
    return urlsafe_base64_encode(force_bytes(user_id))

def decode_user_id(encoded_id):
    """Decode a user ID from a verification URL."""
    try:
        return force_str(urlsafe_base64_decode(encoded_id))
    except (TypeError, ValueError, OverflowError):
        return None
