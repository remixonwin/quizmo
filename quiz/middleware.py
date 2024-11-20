from django.utils.deprecation import MiddlewareMixin
import re
from django.middleware.security import SecurityMiddleware
from django.http import HttpResponsePermanentRedirect

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Add security headers
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()'
        
        # Add CSP header
        csp_policies = [
            "default-src 'self'",
            "img-src 'self' data: https:",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "font-src 'self' https://cdn.jsdelivr.net",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "base-uri 'self'",
            "object-src 'none'"
        ]
        response['Content-Security-Policy'] = '; '.join(csp_policies)
        
        return response

class AdminAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the request is for the admin interface
        if re.match(r'^/quiz-management-portal/', request.path):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Add your IP address checks here
            # allowed_ips = ['127.0.0.1', 'your.ip.address']
            # if ip not in allowed_ips:
            #     raise PermissionDenied

class CustomSecurityMiddleware(SecurityMiddleware):
    def process_request(self, request):
        # Skip SSL redirect for health check endpoint
        if request.path.rstrip('/') == '/health':
            return None
        return super().process_request(request)
