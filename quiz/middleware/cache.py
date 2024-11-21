"""
Cache Control Middleware
Implements caching strategies and headers for optimized performance.
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse
from typing import Optional, Set
import re


class CacheControlMiddleware(MiddlewareMixin):
    """
    Middleware to manage cache control headers for different types of content.
    Implements intelligent caching strategies based on content type and URL patterns.
    """

    # Cache settings for different content types
    STATIC_CACHE_TIMEOUT = 31536000  # 1 year for static files
    DYNAMIC_CACHE_TIMEOUT = 300      # 5 minutes for dynamic content
    NO_CACHE_PATHS = {
        r'^/api/',                   # API endpoints
        r'^/quiz-management-portal/', # Admin interface
        r'/submit/',                 # Form submissions
        r'/results/',                # Quiz results
    }

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.no_cache_patterns = [re.compile(pattern) for pattern in self.NO_CACHE_PATHS]

    def _is_no_cache_path(self, path: str) -> bool:
        """Check if path matches any no-cache patterns."""
        return any(pattern.match(path) for pattern in self.no_cache_patterns)

    def _is_static_file(self, path: str) -> bool:
        """Determine if path is for a static file."""
        static_extensions = {'.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.woff', '.woff2'}
        return any(path.endswith(ext) for ext in static_extensions)

    def _get_cache_headers(self, request: HttpRequest) -> dict:
        """
        Generate appropriate cache headers based on request characteristics.
        """
        path = request.path.lower()

        # No cache for specified paths
        if self._is_no_cache_path(path):
            return {
                'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
                'Pragma': 'no-cache',
                'Expires': '0',
            }

        # Aggressive caching for static files
        if self._is_static_file(path):
            return {
                'Cache-Control': f'public, max-age={self.STATIC_CACHE_TIMEOUT}, immutable',
                'Pragma': 'cache',
            }

        # Default caching for dynamic content
        return {
            'Cache-Control': f'public, max-age={self.DYNAMIC_CACHE_TIMEOUT}, must-revalidate',
            'Pragma': 'cache',
        }

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Apply cache headers to response."""
        # Skip if response already has cache headers
        if 'Cache-Control' in response:
            return response

        # Apply cache headers based on request/response characteristics
        cache_headers = self._get_cache_headers(request)
        for header, value in cache_headers.items():
            response[header] = value

        return response
