"""
System metrics collection and monitoring.
"""
from typing import Dict, Any
import psutil
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class SystemMetrics:
    """System metrics collection with caching."""
    
    CACHE_KEY_PREFIX = 'system_metrics'
    CACHE_TIMEOUT = getattr(settings, 'SYSTEM_METRICS_CACHE_TIME', 60)  # 1 minute default
    
    @classmethod
    def get_cpu_metrics(cls) -> Dict[str, Any]:
        """Get CPU metrics."""
        try:
            return {
                'percent': psutil.cpu_percent(interval=1),
                'cores': psutil.cpu_count(),
                'load_avg': psutil.getloadavg()
            }
        except Exception as e:
            logger.error(f"Failed to get CPU metrics: {str(e)}")
            return {}

    @classmethod
    def get_memory_metrics(cls) -> Dict[str, Any]:
        """Get memory metrics."""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free
            }
        except Exception as e:
            logger.error(f"Failed to get memory metrics: {str(e)}")
            return {}

    @classmethod
    def get_disk_metrics(cls) -> Dict[str, Any]:
        """Get disk metrics."""
        try:
            disk = psutil.disk_usage('/')
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except Exception as e:
            logger.error(f"Failed to get disk metrics: {str(e)}")
            return {}

    @classmethod
    def get_network_metrics(cls) -> Dict[str, Any]:
        """Get network metrics."""
        try:
            network = psutil.net_io_counters()
            return {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
        except Exception as e:
            logger.error(f"Failed to get network metrics: {str(e)}")
            return {}

    @classmethod
    def get_all_metrics(cls) -> Dict[str, Any]:
        """Get all system metrics with caching."""
        cache_key = f'{cls.CACHE_KEY_PREFIX}_all'
        metrics = cache.get(cache_key)
        
        if metrics is None:
            try:
                metrics = {
                    'cpu': cls.get_cpu_metrics(),
                    'memory': cls.get_memory_metrics(),
                    'disk': cls.get_disk_metrics(),
                    'network': cls.get_network_metrics(),
                    'timestamp': psutil.time.time()
                }
                cache.set(cache_key, metrics, cls.CACHE_TIMEOUT)
                
            except Exception as e:
                logger.error(f"Failed to get system metrics: {str(e)}")
                metrics = {}
        
        return metrics
