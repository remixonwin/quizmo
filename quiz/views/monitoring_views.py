"""
Views for application monitoring and health checks.
"""
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from typing import Dict, Any
import logging
from ..monitoring import SystemMetrics, HealthCheck, DatabaseHealth, CacheHealth
from django.conf import settings

logger = logging.getLogger(__name__)

@never_cache
@require_http_methods(['GET'])
def health_check(request) -> JsonResponse:
    """Overall application health check endpoint."""
    return JsonResponse(HealthCheck.get_full_status())

@never_cache
@require_http_methods(['GET'])
def database_health(request) -> JsonResponse:
    """Database health check endpoint."""
    return JsonResponse(DatabaseHealth.check())

@never_cache
@require_http_methods(['GET'])
def cache_health(request) -> JsonResponse:
    """Cache health check endpoint."""
    return JsonResponse(CacheHealth.check())

@never_cache
@require_http_methods(['GET'])
@gzip_page
def system_metrics(request) -> JsonResponse:
    """System metrics endpoint."""
    return JsonResponse(SystemMetrics.get_all_metrics())

@never_cache
@require_http_methods(['GET'])
def test_error_page(request):
    """View for testing error pages in development."""
    if not settings.DEBUG:
        raise Http404("Test error page only available in debug mode")
    
    error_type = request.GET.get('type', '500')
    template = f'errors/{error_type}.html'
    
    return render(request, template, {
        'error_message': 'Test error page',
        'request_id': 'test-request-id',
        'user_agent': request.META.get('HTTP_USER_AGENT', 'N/A'),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }, status=int(error_type))

@never_cache
@require_http_methods(['GET'])
def preview_page(request):
    """Preview page for testing UI components."""
    if not settings.DEBUG:
        raise Http404("Preview page only available in debug mode")
    
    context = {
        'components': [
            {'name': 'Buttons', 'template': 'components/buttons.html'},
            {'name': 'Forms', 'template': 'components/forms.html'},
            {'name': 'Cards', 'template': 'components/cards.html'},
            {'name': 'Alerts', 'template': 'components/alerts.html'}
        ],
        'colors': settings.THEME_COLORS if hasattr(settings, 'THEME_COLORS') else {},
        'debug': settings.DEBUG,
        'sample_data': {
            'title': 'Sample Title',
            'description': 'Sample description for testing UI components.'
        }
    }
    
    return render(request, 'preview/components.html', context)
