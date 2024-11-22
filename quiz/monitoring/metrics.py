"""
System metrics collection for the quiz application.
"""
from django.db import connection
from django.core.cache import cache
import psutil
import logging
import time

logger = logging.getLogger(__name__)

class SystemMetrics:
    """System metrics collection and monitoring."""
    
    @classmethod
    def collect_metrics(cls):
        """Collect system metrics."""
        metrics = {
            'system': cls.get_system_metrics(),
            'database': cls.get_database_metrics(),
            'cache': cls.get_cache_metrics(),
        }
        return metrics
    
    @staticmethod
    def get_system_metrics():
        """Get system resource metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': disk.percent,
                'disk_free': disk.free,
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    @staticmethod
    def get_database_metrics():
        """Get database connection metrics."""
        try:
            with connection.cursor() as cursor:
                start_time = time.time()
                cursor.execute("SELECT 1")
                query_time = time.time() - start_time
                
                return {
                    'connection_count': len(connection.connection.queries),
                    'query_time': query_time,
                }
        except Exception as e:
            logger.error(f"Failed to collect database metrics: {e}")
            return {}
    
    @staticmethod
    def get_cache_metrics():
        """Get cache metrics."""
        try:
            start_time = time.time()
            cache.get('test_key')
            cache_time = time.time() - start_time
            
            return {
                'cache_time': cache_time,
            }
        except Exception as e:
            logger.error(f"Failed to collect cache metrics: {e}")
            return {}
