"""
Health check views for monitoring application status.
"""
from django.db import connections
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import logging
import psutil
import redis

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check endpoint that verifies:
    1. Database connection
    2. Redis connection
    3. Application status
    4. System resources
    """
    health_status = {
        'status': 'healthy',
        'database': True,
        'cache': True,
        'system': {
            'cpu_usage': None,
            'memory_usage': None,
        }
    }

    # Check database connection
    try:
        for name in connections:
            cursor = connections[name].cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status['database'] = False
        health_status['status'] = 'unhealthy'

    # Check Redis connection
    try:
        cache.set('health_check', 'ok', 1)
        if cache.get('health_check') != 'ok':
            raise redis.RedisError("Cache check failed")
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_status['cache'] = False
        health_status['status'] = 'unhealthy'

    # Check system resources
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        health_status['system'] = {
            'cpu_usage': f"{cpu_usage}%",
            'memory_usage': f"{memory.percent}%"
        }

        # Mark as unhealthy if resources are critically low
        if cpu_usage > 95 or memory.percent > 95:
            health_status['status'] = 'degraded'
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        health_status['status'] = 'degraded'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
