
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled

def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats throttled exceptions with an 'error' field.
    """
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        response.data = {'error': 'Too many password reset requests. Please try again later.'}
        response.status_code = 429

    return response