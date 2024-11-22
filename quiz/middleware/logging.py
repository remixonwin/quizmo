"""
Logging middleware for the quiz application.
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class LoggingMiddleware(MiddlewareMixin):
    """Middleware for request/response logging."""
    
    def __init__(self, get_response):
        """Initialize middleware."""
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """Process and log incoming request."""
        # Generate request ID if not present
        request.id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
        
        # Log request details
        self._log_request(request)
        
        return None
    
    def process_response(self, request, response):
        """Process and log outgoing response."""
        # Log response details
        self._log_response(request, response)
        
        # Add request ID to response headers
        response['X-Request-ID'] = request.id
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions during request processing."""
        logger.error(
            "Exception during request processing",
            exc_info=True,
            extra={
                'request_id': request.id,
                'method': request.method,
                'path': request.path,
                'user_id': getattr(request.user, 'id', None),
                'exception': str(exception),
            }
        )
        return None
    
    def _log_request(self, request):
        """Log request details."""
        try:
            body = None
            if request.body and settings.DEBUG:
                try:
                    body = json.loads(request.body)
                except json.JSONDecodeError:
                    body = request.body.decode('utf-8')
            
            logger.info(
                "Request received",
                extra={
                    'request_id': request.id,
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET),
                    'body': body if settings.DEBUG else None,
                    'headers': dict(request.headers),
                    'user_id': getattr(request.user, 'id', None),
                    'ip': request.META.get('REMOTE_ADDR'),
                }
            )
        except Exception as e:
            logger.error(f"Error logging request: {e}")
    
    def _log_response(self, request, response):
        """Log response details."""
        try:
            logger.info(
                "Response sent",
                extra={
                    'request_id': request.id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'content_type': response.get('Content-Type', ''),
                    'content_length': len(response.content) if hasattr(response, 'content') else 0,
                    'user_id': getattr(request.user, 'id', None),
                }
            )
        except Exception as e:
            logger.error(f"Error logging response: {e}")
