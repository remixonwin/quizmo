"""
Access Control Middleware
Implements access control and rate limiting for various endpoints.
"""

import re
from typing import Optional, Set
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class AdminAccessMiddleware(MiddlewareMixin):
    """Controls access to admin interface based on IP and rate limiting."""

    ADMIN_URL_PATTERN = r'^/quiz-management-portal/'
    RATE_LIMIT_KEY_PREFIX = 'admin_access_'
    MAX_ATTEMPTS = 5
    BLOCK_DURATION = 300  # 5 minutes in seconds

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.allowed_ips: Set[str] = self._get_allowed_ips()
        self.admin_pattern = re.compile(self.ADMIN_URL_PATTERN)

    @staticmethod
    def _get_allowed_ips() -> Set[str]:
        """Get allowed IPs from settings with fallback to defaults."""
        return set(getattr(settings, 'ADMIN_ALLOWED_IPS', ['127.0.0.1']))

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP from request with proxy support."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

    def _check_rate_limit(self, ip: str) -> bool:
        """
        Check if IP has exceeded rate limit.
        Returns True if allowed, False if blocked.
        """
        key = f"{self.RATE_LIMIT_KEY_PREFIX}{ip}"
        attempts = cache.get(key, 0)

        if attempts >= self.MAX_ATTEMPTS:
            return False

        # Increment attempts
        if attempts == 0:
            cache.set(key, 1, self.BLOCK_DURATION)
        else:
            cache.incr(key)

        return True

    def process_request(self, request: HttpRequest) -> Optional[None]:
        """Process request for admin access control."""
        # Only check admin URLs
        if not self.admin_pattern.match(request.path):
            return None

        client_ip = self._get_client_ip(request)

        # Check IP allowlist
        if client_ip not in self.allowed_ips:
            # Check rate limit before denying access
            if not self._check_rate_limit(client_ip):
                raise PermissionDenied("Too many access attempts. Please try again later.")
            raise PermissionDenied("Access denied.")

        return None
