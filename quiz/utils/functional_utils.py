"""
Functional utilities for authentication.
"""
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar
from dataclasses import dataclass
from functools import partial, reduce, wraps
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse

T = TypeVar('T')
R = TypeVar('R')

@dataclass(frozen=True)
class AuthResult:
    """Immutable result of an authentication operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    redirect_to: Optional[str] = None
    template: Optional[str] = None
    status_code: Optional[int] = None

def compose(*functions: Callable) -> Callable:
    """Compose multiple functions from right to left."""
    return reduce(lambda f, g: lambda x: f(g(x)), functions)

def pipe(value: T, *functions: Callable[[T], T]) -> T:
    """Pipe a value through a series of functions from left to right."""
    return reduce(lambda acc, fn: fn(acc), functions, value)

def with_logging(logger):
    """Decorator to add logging to functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if isinstance(result, AuthResult) and not result.success:
                    logger.warning(f"{func.__name__} failed: {result.message}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator

def handle_auth_result(request: HttpRequest, result: AuthResult) -> HttpResponse:
    """Handle AuthResult and return appropriate HttpResponse."""
    if result.message:
        message_func = messages.success if result.success else messages.error
        message_func(request, result.message)
    
    if result.redirect_to:
        # Handle both URL names and direct paths
        redirect_url = result.redirect_to
        if ':' in redirect_url:  # It's a URL name
            redirect_url = reverse(redirect_url)
        elif request.GET.get('next'):  # Honor next parameter
            redirect_url = request.GET.get('next')
        response = redirect(redirect_url)
        if result.status_code:
            response.status_code = result.status_code
        return response
    elif result.template:
        context = result.data or {}
        response = render(request, result.template, context)
        if result.status_code:
            response.status_code = result.status_code
        return response
    
    # Default redirect to dashboard
    response = redirect('quiz:dashboard')
    if result.status_code:
        response.status_code = result.status_code
    return response

def cache_get(key: str, default: T = None) -> T:
    """Functional wrapper for cache.get."""
    return cache.get(key, default)

def cache_set(key: str, value: T, timeout: int = None) -> None:
    """Functional wrapper for cache.set."""
    cache.set(key, value, timeout)

def cache_delete(key: str) -> None:
    """Functional wrapper for cache.delete."""
    cache.delete(key)

def get_client_ip(request: HttpRequest) -> str:
    """Get client IP address from request in a functional way."""
    return pipe(
        request.META.get('HTTP_X_FORWARDED_FOR', ''),
        lambda x: x.split(',')[0] if x else request.META.get('REMOTE_ADDR', '')
    )

def check_login_attempts(ip_address: str) -> bool:
    """Check login attempts in a functional way."""
    return pipe(
        f'login_attempts_{ip_address}',
        lambda key: cache_get(key, 0),
        lambda attempts: attempts >= settings.MAX_LOGIN_ATTEMPTS
    )

def increment_login_attempts(ip_address: str) -> None:
    """Increment login attempts in a functional way."""
    key = f'login_attempts_{ip_address}'
    pipe(
        cache_get(key, 0),
        lambda attempts: attempts + 1,
        lambda attempts: cache_set(key, attempts, settings.ACCOUNT_LOCKOUT_DURATION)
    )

def reset_login_attempts(ip_address: str) -> None:
    """Reset login attempts in a functional way."""
    pipe(
        f'login_attempts_{ip_address}',
        cache_delete
    )

def validate_request(validator: Callable[[HttpRequest], Tuple[bool, Optional[str]]]):
    """Decorator to validate request and return AuthResult."""
    def decorator(func):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            is_valid, error = validator(request)
            if not is_valid:
                if error:
                    messages.error(request, error)
                return handle_auth_result(request, AuthResult(
                    success=False,
                    message=error or '',
                    template=getattr(settings, 'DEFAULT_ERROR_TEMPLATE', 'quiz/auth/error.html'),
                    status_code=400  # Bad Request for validation errors
                ))
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def with_transaction(func: Callable[[], AuthResult]) -> Callable[[], AuthResult]:
    """Decorator to handle database transactions."""
    from django.db import transaction
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                return func(*args, **kwargs)
        except Exception as e:
            return AuthResult(
                success=False,
                message=str(e),
                template=getattr(settings, 'DEFAULT_ERROR_TEMPLATE', 'quiz/auth/error.html'),
                status_code=500  # Internal Server Error for exceptions
            )
    return wrapper
