"""
Health checks for the quiz application.
"""
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class HealthCheck:
    """Base health check class."""
    
    @classmethod
    def check_health(cls):
        """Run all health checks."""
        health_status = {
            'status': 'healthy',
            'checks': {
                'database': DatabaseHealth.check(),
                'cache': CacheHealth.check(),
            }
        }
        
        # If any check failed, mark overall status as unhealthy
        if any(not check['healthy'] for check in health_status['checks'].values()):
            health_status['status'] = 'unhealthy'
        
        return health_status

class DatabaseHealth:
    """Database health check."""
    
    @staticmethod
    def check():
        """Check database connection health."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return {
                    'healthy': True,
                    'message': 'Database connection successful'
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'healthy': False,
                'message': f'Database connection failed: {str(e)}'
            }

class CacheHealth:
    """Cache health check."""
    
    @staticmethod
    def check():
        """Check cache connection health."""
        try:
            cache.set('health_check', True, 10)
            result = cache.get('health_check')
            cache.delete('health_check')
            
            if result is True:
                return {
                    'healthy': True,
                    'message': 'Cache connection successful'
                }
            else:
                return {
                    'healthy': False,
                    'message': 'Cache get operation failed'
                }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                'healthy': False,
                'message': f'Cache connection failed: {str(e)}'
            }
