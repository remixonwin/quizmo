"""
System monitoring module for tracking application health and performance.
"""
import os
import psutil
import logging
from django.db import connections
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import json

logger = logging.getLogger('performance')

class SystemMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.metrics_file = os.path.join(settings.BASE_DIR, 'logs', 'metrics', 'system_metrics.json')
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)

    def get_system_metrics(self):
        """Get system-wide metrics."""
        return {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': dict(psutil.virtual_memory()._asdict()),
            'disk_usage': dict(psutil.disk_usage('/')._asdict()),
            'network_io': dict(psutil.net_io_counters()._asdict()),
        }

    def get_application_metrics(self):
        """Get application-specific metrics."""
        with self.process.oneshot():
            return {
                'app_cpu_usage': self.process.cpu_percent(),
                'app_memory_usage': dict(self.process.memory_info()._asdict()),
                'app_threads': self.process.num_threads(),
                'app_open_files': len(self.process.open_files()),
                'app_connections': len(self.process.connections()),
            }

    def get_database_metrics(self):
        """Get database connection metrics."""
        metrics = {}
        for alias in connections:
            connection = connections[alias]
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    metrics[alias] = {
                        'status': 'connected',
                        'queries': len(connection.queries) if settings.DEBUG else 'N/A',
                    }
            except Exception as e:
                metrics[alias] = {
                    'status': 'error',
                    'error': str(e),
                }
        return metrics

    def get_cache_metrics(self):
        """Get cache metrics."""
        try:
            test_key = '_test_cache_key'
            cache.set(test_key, 'test', 10)
            cache_value = cache.get(test_key)
            cache.delete(test_key)
            return {
                'status': 'operational' if cache_value == 'test' else 'error',
                'backend': settings.CACHES['default']['BACKEND'],
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
            }

    def collect_metrics(self):
        """Collect all system and application metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_metrics(),
            'application': self.get_application_metrics(),
            'database': self.get_database_metrics(),
            'cache': self.get_cache_metrics(),
        }

        # Save metrics to file with rotation
        self._save_metrics(metrics)
        return metrics

    def _save_metrics(self, metrics):
        """Save metrics to file with rotation."""
        try:
            # Create metrics directory if it doesn't exist
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)

            # Load existing metrics
            existing_metrics = []
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    existing_metrics = json.load(f)

            # Add new metrics
            existing_metrics.append(metrics)

            # Keep only last 24 hours of metrics
            cutoff_time = datetime.now() - timedelta(hours=24)
            existing_metrics = [
                m for m in existing_metrics
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]

            # Save updated metrics
            with open(self.metrics_file, 'w') as f:
                json.dump(existing_metrics, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def get_health_status(self):
        """
        Get overall system health status with warnings and critical issues.
        """
        try:
            metrics = self.collect_metrics()
            warnings = []
            critical = []
            
            # Check CPU usage
            if metrics['system']['cpu_usage'] > 90:
                critical.append('CPU usage is critically high')
            elif metrics['system']['cpu_usage'] > 75:
                warnings.append('CPU usage is high')
            
            # Check memory usage
            memory_percent = metrics['system']['memory_usage']['percent']
            if memory_percent > 90:
                critical.append('Memory usage is critically high')
            elif memory_percent > 75:
                warnings.append('Memory usage is high')
            
            # Check disk usage
            disk_percent = metrics['system']['disk_usage']['percent']
            if disk_percent > 90:
                critical.append('Disk usage is critically high')
            elif disk_percent > 75:
                warnings.append('Disk usage is high')
            
            # Determine overall status
            status = 'healthy'
            if critical:
                status = 'critical'
            elif warnings:
                status = 'warning'
            
            return {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'warnings': warnings,
                'critical': critical,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'warnings': [],
                'critical': [str(e)],
                'metrics': {}
            }
