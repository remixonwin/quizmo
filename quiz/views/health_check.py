"""
Health check endpoints for monitoring system status.
"""
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.conf import settings
import logging
from ..monitoring.system_monitor import SystemMonitor

logger = logging.getLogger('performance')
system_monitor = SystemMonitor()

@never_cache
@require_GET
def health_check(request):
    """
    Basic health check endpoint that returns system status.
    """
    try:
        health_status = system_monitor.get_health_status()
        status_code = {
            'healthy': 200,
            'warning': 200,
            'critical': 503,
        }.get(health_status['status'], 500)

        response = {
            'status': health_status['status'],
            'timestamp': health_status['timestamp'],
        }

        # Include warnings and critical issues if they exist
        if health_status['warnings']:
            response['warnings'] = health_status['warnings']
        if health_status['critical']:
            response['critical'] = health_status['critical']

        # Include detailed metrics in debug mode
        if settings.DEBUG:
            response['metrics'] = health_status['metrics']

        return JsonResponse(response, status=status_code)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Health check failed',
            'error': str(e) if settings.DEBUG else 'Internal server error'
        }, status=500)

@never_cache
@require_GET
def detailed_health_check(request):
    """
    Detailed health check endpoint that returns comprehensive system metrics.
    Requires staff user authentication.
    """
    if not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'Unauthorized access'
        }, status=403)

    try:
        metrics = system_monitor.collect_metrics()
        return JsonResponse({
            'status': 'success',
            'data': metrics
        })
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Detailed health check failed',
            'error': str(e) if settings.DEBUG else 'Internal server error'
        }, status=500)
