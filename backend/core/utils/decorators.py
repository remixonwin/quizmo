from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import time

def retry_on_error(retries=3, delay=1):
    """Decorator to retry a function on failure with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries - 1:
                        raise
                    time.sleep(delay * (2 ** i))
        return wrapper
    return decorator

def atomic_transaction():
    """Decorator to wrap a view method in a database transaction"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_exceptions(func):
    """Decorator to handle common API exceptions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ObjectDoesNotExist as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Internal server error', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

def validate_request_data(required_fields):
    """Decorator to validate required fields in request data"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            missing_fields = [
                field for field in required_fields 
                if field not in request.data
            ]
            if missing_fields:
                return Response(
                    {
                        'error': 'Missing required fields',
                        'fields': missing_fields
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator

__all__ = [
    'retry_on_error',
    'atomic_transaction', 
    'handle_exceptions',
    'validate_request_data'
]