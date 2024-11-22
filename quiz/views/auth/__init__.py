"""
Authentication views package.
"""
from .login import login_view
from .register import register_view
from .password import password_reset_view, password_reset_confirm_view
from .profile import profile, dashboard
from .verification import verify_email
from .logout import logout_view

__all__ = [
    'login_view',
    'register_view',
    'password_reset_view',
    'password_reset_confirm_view',
    'profile',
    'dashboard',
    'verify_email',
    'logout_view',
]
