"""
Rate limiting middleware for the quiz application.
"""
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time
import hashlib
import logging

logger = logging.getLogger(__name__)

class HttpResponseTooManyRequests(HttpResponse):
    """429 Too Many Requests response"""
    status_code = 429

class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware for request throttling."""
    
    # Default rate limits
    DEFAULT_RATE_LIMITS = {
        'DEFAULT': {'rate': 60, 'period': 60},  # 60 requests per minute
        'AUTH': {'rate': 5, 'period': 300},     # 5 requests per 5 minutes
        'QUIZ': {'rate': 30, 'period': 3600},   # 30 requests per hour
    }
    
    def __init__(self, get_response):
        """Initialize middleware."""
        super().__init__(get_response)
        self.get_response = get_response
        self.rate_limits = getattr(settings, 'RATE_LIMITS', self.DEFAULT_RATE_LIMITS)
    
    def process_request(self, request):
        """Process request and apply rate limiting."""
        # Skip rate limiting in debug mode
        if settings.DEBUG:
            return None
            
        # Get rate limit type based on path
        limit_type = self._get_limit_type(request)
        limit_config = self.rate_limits.get(limit_type, self.rate_limits['DEFAULT'])
        
        # Generate cache key
        key = self._get_cache_key(request, limit_type)
        
        # Check rate limit
        if self._is_rate_limited(key, limit_config):
            logger.warning(
                "Rate limit exceeded",
                extra={
                    'ip': request.META.get('REMOTE_ADDR'),
                    'path': request.path,
                    'user_id': getattr(request.user, 'id', None),
                    'limit_type': limit_type,
                }
            )
            return HttpResponseTooManyRequests("Rate limit exceeded")
        
        return None
    
    def _get_limit_type(self, request):
        """Determine rate limit type based on request path."""
        path = request.path.lower()
        
        if path.startswith('/auth/') or path.startswith('/api/auth/'):
            return 'AUTH'
        elif path.startswith('/quiz/') or path.startswith('/api/quiz/'):
            return 'QUIZ'
        
        return 'DEFAULT'
    
    def _get_cache_key(self, request, limit_type):
        """Generate cache key for rate limiting."""
        # Use IP and user ID if available
        identifiers = [
            request.META.get('REMOTE_ADDR', ''),
            str(getattr(request.user, 'id', '')),
            limit_type
        ]
        
        # Create unique key
        key_string = ':'.join(filter(None, identifiers))
        return f'ratelimit:{hashlib.md5(key_string.encode()).hexdigest()}'
    
    def _is_rate_limited(self, key, limit_config):
        """Check if request should be rate limited."""
        try:
            rate = limit_config['rate']
            period = limit_config['period']
            
            pipe = cache.pipeline()
            now = time.time()
            
            # Get current request count
            request_count = cache.get(key, 0)
            
            if request_count >= rate:
                return True
            
            # Increment request count
            pipe.incr(key)
            pipe.expire(key, period)
            pipe.execute()
            
            return False
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return False  # Fail open on errors
