"""
Health check implementations for application components.
"""
from typing import Dict, Any, Optional
import logging
import time
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from .metrics import SystemMetrics

logger = logging.getLogger(__name__)

class HealthCheck:
    """Base health check implementation."""
    
    TIMEOUT = getattr(settings, 'HEALTH_CHECK_TIMEOUT', 30)  # seconds
    CACHE_KEY_PREFIX = 'health'
    
    @classmethod
    def check_component(cls, component_name: str, check_func) -> Dict[str, Any]:
        """
        Generic component health check with timing.
        
        Args:
            component_name: Name of component being checked
            check_func: Function to check component health
            
        Returns:
            Health check results with timing
        """
        start_time = time.time()
        status = 'healthy'
        error = None
        
        try:
            check_func()
        except Exception as e:
            status = 'unhealthy'
            error = str(e)
            logger.error(f"{component_name} health check failed: {error}")
        
        elapsed = time.time() - start_time
        
        return {
            'status': status,
            'responseTime': elapsed,
            'error': error
        }

    @classmethod
    def get_full_status(cls) -> Dict[str, Any]:
        """Get full application health status."""
        return {
            'status': 'ok',
            'database': DatabaseHealth.check(),
            'cache': CacheHealth.check(),
            'system': SystemMetrics.get_all_metrics()
        }


class DatabaseHealth(HealthCheck):
    """Database health check implementation."""
    
    @classmethod
    def check(cls) -> Dict[str, Any]:
        """Check database health."""
        def check_db():
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        
        return cls.check_component('Database', check_db)


class CacheHealth(HealthCheck):
    """Cache health check implementation."""
    
    @classmethod
    def check(cls) -> Dict[str, Any]:
        """Check cache health."""
        def check_cache():
            key = f'{cls.CACHE_KEY_PREFIX}_test'
            cache.set(key, 'test', 1)
            cache.get(key)
            cache.delete(key)
        
        return cls.check_component('Cache', check_cache)
