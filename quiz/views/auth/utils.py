"""
Authentication utility functions.
"""
from django.core.cache import cache
from django.conf import settings

def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_login_attempts(ip_address):
    """Check if the IP has exceeded the maximum login attempts."""
    attempts = cache.get(f'login_attempts_{ip_address}', 0)
    return attempts >= settings.MAX_LOGIN_ATTEMPTS

def increment_login_attempts(ip_address):
    """Increment the number of login attempts for an IP."""
    attempts = cache.get(f'login_attempts_{ip_address}', 0)
    attempts += 1
    cache.set(
        f'login_attempts_{ip_address}',
        attempts,
        settings.ACCOUNT_LOCKOUT_DURATION
    )

def reset_login_attempts(ip_address):
    """Reset login attempts for an IP."""
    cache.delete(f'login_attempts_{ip_address}')
