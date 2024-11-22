"""
Security utilities for the quiz app.
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import hashlib
import hmac
import base64

def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def generate_token(length=32):
    """Generate a secure random token."""
    return get_random_string(length)

def hash_password(password, salt=None):
    """Hash a password using PBKDF2 with SHA256."""
    if not salt:
        salt = get_random_string(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000,
        dklen=32
    )
    return base64.b64encode(key).decode(), salt

def verify_password(password, hashed_password, salt):
    """Verify a password against its hash."""
    new_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(
        new_hash.encode(),
        hashed_password.encode()
    )

class TokenGenerator(PasswordResetTokenGenerator):
    """Custom token generator for email verification."""
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active)
        )

account_activation_token = TokenGenerator()

def encode_uid(pk):
    """Encode user ID for verification URL."""
    return urlsafe_base64_encode(force_bytes(pk))

def decode_uid(uidb64):
    """Decode user ID from verification URL."""
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except (TypeError, ValueError, OverflowError):
        return None
