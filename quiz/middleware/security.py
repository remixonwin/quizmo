"""
Security middleware for the quiz application.
"""
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import logging
from django.urls import resolve, Resolver404
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse

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
    
    PUBLIC_PATHS = {
        'quiz:login',
        'quiz:register',
        'quiz:password_reset',
        'quiz:password_reset_done',
        'quiz:password_reset_confirm',
        'quiz:password_reset_complete',
        'quiz:verify_email',
        'quiz:help',
        'quiz:faq',
        'quiz:study_materials',
        'quiz:logout',  
        'admin:login',
        'admin:logout',  
    }
    
    def __init__(self, get_response):
        """Initialize middleware."""
        super().__init__(get_response)
        self.get_response = get_response
    
    def is_public_path(self, request):
        """Check if the current path is a public path."""
        try:
            resolved = resolve(request.path_info)
            url_name = resolved.url_name
            namespace = resolved.namespace
            full_url_name = f"{namespace}:{url_name}" if namespace else url_name
            return full_url_name in self.PUBLIC_PATHS
        except Resolver404:
            return False
            
    def process_request(self, request):
        """Process incoming request."""
        # Allow all requests in debug mode
        if settings.DEBUG:
            return None
            
        # Check if this is a public path
        if self.is_public_path(request):
            return None
            
        # For non-public paths, require authentication
        if not request.user.is_authenticated:
            next_url = request.get_full_path()
            login_url = f"{reverse('quiz:login')}?next={next_url}"
            return redirect(login_url)
            
        # For authenticated users on non-public paths, require HTTPS in production
        if not settings.DEBUG and not request.is_secure():
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
        logger.error(f"Security middleware caught exception: {str(exception)}")
        return None
