"""
Request Monitoring Middleware
Implements request monitoring, logging, and performance tracking.
"""

import time
import logging
from typing import Optional
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

# Configure logger
logger = logging.getLogger('quiz.monitoring')


class RequestMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware for monitoring request performance and logging.
    Tracks request timing, errors, and key metrics.
    """

    # Thresholds for performance monitoring (in seconds)
    SLOW_REQUEST_THRESHOLD = 1.0
    VERY_SLOW_REQUEST_THRESHOLD = 3.0

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.enable_detailed_logging = getattr(settings, 'ENABLE_DETAILED_REQUEST_LOGGING', False)

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Start timing the request and initialize tracking."""
        request.start_time = time.time()
        return None

    def _log_request_metrics(self, request: HttpRequest, response: HttpResponse, duration: float):
        """Log request metrics based on duration and status."""
        log_data = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration': f"{duration:.3f}s",
            'ip': self._get_client_ip(request),
        }

        # Add detailed logging if enabled
        if self.enable_detailed_logging:
            log_data.update({
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', ''),
                'content_length': len(response.content) if hasattr(response, 'content') else 0,
            })

        # Determine log level based on response status and duration
        if response.status_code >= 500:
            logger.error("Server error", extra=log_data)
        elif response.status_code >= 400:
            logger.warning("Client error", extra=log_data)
        elif duration > self.VERY_SLOW_REQUEST_THRESHOLD:
            logger.warning("Very slow request", extra=log_data)
        elif duration > self.SLOW_REQUEST_THRESHOLD:
            logger.info("Slow request", extra=log_data)
        else:
            logger.debug("Request completed", extra=log_data)

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """Extract client IP from request with proxy support."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Calculate request duration and log metrics."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            self._log_request_metrics(request, response, duration)

            # Add server timing header
            response['Server-Timing'] = f'total;dur={duration * 1000:.0f}'

        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Log unhandled exceptions."""
        logger.exception(
            "Unhandled exception in request",
            extra={
                'method': request.method,
                'path': request.path,
                'ip': self._get_client_ip(request),
                'exception': str(exception),
            }
        )
