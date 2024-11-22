"""
Security middleware for the quiz application.
"""
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(MiddlewareMixin):
    """Security middleware for request/response processing."""
    
    SECURE_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()',
    }
    
    def __init__(self, get_response):
        """Initialize middleware."""
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """Process incoming request."""
        # Check for required security headers
        if not settings.DEBUG:
            if not request.is_secure():
                return HttpResponseForbidden("HTTPS Required")
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing response."""
        # Add security headers
        for header, value in self.SECURE_HEADERS.items():
            if header not in response:
                response[header] = value
        
        # Add HSTS header in production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Remove sensitive headers
        response.headers.pop('Server', None)
        response.headers.pop('X-Powered-By', None)
        
        return response
    
    def process_exception(self, request, exception):
        """Handle exceptions during request processing."""
        logger.error(f"Security middleware caught exception: {exception}")
        return None
