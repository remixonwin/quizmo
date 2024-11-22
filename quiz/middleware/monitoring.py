"""
Monitoring middleware for the quiz application.
"""
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.conf import settings
from ..monitoring.metrics import SystemMetrics
import logging
import time

logger = logging.getLogger(__name__)

class MonitoringMiddleware(MiddlewareMixin):
    """Middleware for monitoring request/response cycle."""
    
    def __init__(self, get_response):
        """Initialize middleware."""
        super().__init__(get_response)
        self.get_response = get_response
        self.metrics = SystemMetrics()
    
    def process_request(self, request):
        """Process incoming request."""
        # Add request timestamp
        request.start_time = time.time()
        
        # Log request details
        logger.info(
            "Request started: %s %s",
            request.method,
            request.path,
            extra={
                'request_id': request.META.get('HTTP_X_REQUEST_ID'),
                'user_id': getattr(request.user, 'id', None),
                'ip': request.META.get('REMOTE_ADDR'),
            }
        )
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing response."""
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Request-Time'] = str(duration)
            
            # Log response details
            logger.info(
                "Request finished: %s %s %s in %.3fs",
                request.method,
                request.path,
                response.status_code,
                duration,
                extra={
                    'request_id': request.META.get('HTTP_X_REQUEST_ID'),
                    'user_id': getattr(request.user, 'id', None),
                    'status_code': response.status_code,
                    'duration': duration,
                }
            )
            
            # Collect metrics in production
            if not settings.DEBUG:
                metrics = self.metrics.collect_metrics()
                logger.info("System metrics", extra={'metrics': metrics})
        
        return response
    
    def process_exception(self, request, exception):
        """Handle exceptions during request processing."""
        logger.error(
            "Request failed: %s %s",
            request.method,
            request.path,
            exc_info=True,
            extra={
                'request_id': request.META.get('HTTP_X_REQUEST_ID'),
                'user_id': getattr(request.user, 'id', None),
                'error': str(exception),
            }
        )
        return None
