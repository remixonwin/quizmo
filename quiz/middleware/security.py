"""
Security Middleware Components
Implements various security measures and headers.
"""

from django.utils.deprecation import MiddlewareMixin
from django.middleware.security import SecurityMiddleware
from django.conf import settings
from typing import Dict, List


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Adds security headers to all responses."""

    # Cache CSP policies to avoid rebuilding them on every request
    _csp_policies: List[str] = [
        "default-src 'self'",
        "img-src 'self' data: https:",
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "form-action 'self'",
        "base-uri 'self'",
        "object-src 'none'"
    ]
    _csp_header: str = '; '.join(_csp_policies)

    # Cache common security headers
    _security_headers: Dict[str, str] = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': (
            'accelerometer=(), camera=(), geolocation=(), '
            'gyroscope=(), magnetometer=(), microphone=(), '
            'payment=(), usb=()'
        ),
    }

    def __init__(self, get_response=None):
        super().__init__(get_response)
        # Add environment-specific CSP policies
        if settings.DEBUG:
            self._update_csp_for_debug()

    def _update_csp_for_debug(self):
        """Updates CSP policies for development environment."""
        debug_policies = []
        script_src_values = set()
        
        # Collect all script-src values and non-script-src policies
        for policy in self._csp_policies:
            if policy.startswith('script-src'):
                # Extract values from script-src policy
                values = policy.split(' ')[1:]
                script_src_values.update(values)
            elif not policy.startswith('connect-src'):
                debug_policies.append(policy)
        
        # Add debug-specific script-src values
        script_src_values.add("'unsafe-eval'")
        
        # Create merged script-src policy
        debug_policies.append(f"script-src {' '.join(script_src_values)}")
        
        # Add debug-specific connect-src policy
        debug_policies.append("connect-src 'self' ws://localhost:*")  # For live reload
        
        self._csp_header = '; '.join(debug_policies)

    def process_response(self, request, response):
        """Add security headers to response."""
        # Add common security headers
        for header, value in self._security_headers.items():
            response[header] = value

        # Add CSP header
        response['Content-Security-Policy'] = self._csp_header

        return response


class CustomSecurityMiddleware(SecurityMiddleware):
    """Extends Django's SecurityMiddleware with custom behavior."""

    HEALTH_CHECK_PATH = '/health'

    def process_request(self, request):
        """
        Process request with custom security rules.
        Skips SSL redirect for health check endpoint.
        """
        if request.path.rstrip('/') == self.HEALTH_CHECK_PATH:
            return None
        return super().process_request(request)
