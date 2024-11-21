"""
Middleware Components
Provides backward compatibility imports for middleware components.
All middleware implementations have been moved to the middleware package.
"""

from .middleware.security import SecurityHeadersMiddleware, CustomSecurityMiddleware
from .middleware.access import AdminAccessMiddleware
from .middleware.cache import CacheControlMiddleware
from .middleware.monitoring import RequestMonitoringMiddleware

__all__ = [
    'SecurityHeadersMiddleware',
    'CustomSecurityMiddleware',
    'AdminAccessMiddleware',
    'CacheControlMiddleware',
    'RequestMonitoringMiddleware',
]
