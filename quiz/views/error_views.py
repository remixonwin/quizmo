"""
Views for handling error pages and error logging.
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings
from typing import Dict, Any, Optional
import logging
import json
import time
import traceback

logger = logging.getLogger(__name__)

# Constants
ERROR_CACHE_TIMEOUT = getattr(settings, 'ERROR_CACHE_TIMEOUT', 300)  # 5 minutes
MAX_ERROR_CACHE = getattr(settings, 'MAX_ERROR_CACHE', 1000)


def get_error_context(request, status_code: int) -> Dict[str, Any]:
    """Get context data for error pages with caching."""
    cache_key = f'error_context_{status_code}'
    context = cache.get(cache_key)
    
    if context is None:
        context = {
            'status_code': status_code,
            'request_id': request.META.get('HTTP_X_REQUEST_ID', 'N/A'),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'N/A'),
            'referer': request.META.get('HTTP_REFERER', 'N/A'),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', ''),
            'support_phone': getattr(settings, 'SUPPORT_PHONE', ''),
            'is_debug': settings.DEBUG
        }
        
        if status_code == 403:
            context.update({
                'title': 'Access Denied',
                'message': 'You do not have permission to access this resource.',
                'help_text': 'If you believe this is an error, please contact support.'
            })
        elif status_code == 404:
            context.update({
                'title': 'Page Not Found',
                'message': 'The requested page could not be found.',
                'help_text': 'Please check the URL or navigate using the menu.'
            })
        elif status_code == 500:
            context.update({
                'title': 'Server Error',
                'message': 'An unexpected error occurred.',
                'help_text': 'Our team has been notified. Please try again later.'
            })
        
        cache.set(cache_key, context, ERROR_CACHE_TIMEOUT)
    
    return context


def log_error(request, status_code: int, error_data: Optional[Dict] = None) -> None:
    """Log error details with request information."""
    error_info = {
        'status_code': status_code,
        'path': request.path,
        'method': request.method,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'ip_address': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'referer': request.META.get('HTTP_REFERER'),
        'query_params': dict(request.GET),
        'error_data': error_data
    }
    
    if status_code >= 500:
        logger.error(f'Server Error: {json.dumps(error_info)}')
    else:
        logger.warning(f'Client Error: {json.dumps(error_info)}')


@require_http_methods(["GET"])
def handler403(request, exception=None):
    """Handle 403 Forbidden errors."""
    context = get_error_context(request, 403)
    log_error(request, 403)
    return render(request, 'errors/403.html', context, status=403)


@require_http_methods(["GET"])
def handler404(request, exception=None):
    """Handle 404 Not Found errors."""
    context = get_error_context(request, 404)
    log_error(request, 404)
    return render(request, 'errors/404.html', context, status=404)


@require_http_methods(["GET"])
def handler500(request, exception=None):
    """Handle 500 Server Error."""
    context = get_error_context(request, 500)
    log_error(request, 500, {
        'exception': str(exception) if exception else None,
        'traceback': traceback.format_exc() if exception else None
    })
    return render(request, 'errors/500.html', context, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def log_client_error(request):
    """Log client-side JavaScript errors."""
    try:
        error_data = json.loads(request.body)
        log_error(request, 400, error_data)
        return JsonResponse({'status': 'error_logged'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f'Error logging client error: {str(e)}')
        return JsonResponse({'error': 'Internal server error'}, status=500)


def session_expired(request):
    """Handle session expiration."""
    messages.warning(request, 'Your session has expired. Please start a new quiz.')
    return HttpResponseRedirect(reverse('quiz:quiz_list'))


def quiz_timeout(request, quiz_id):
    """Handle quiz timeout."""
    messages.warning(request, 'Quiz time limit exceeded. Please start a new attempt.')
    return HttpResponseRedirect(reverse('quiz:quiz_detail', args=[quiz_id]))
