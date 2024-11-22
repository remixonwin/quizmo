"""
Monitoring setup for the quiz application.
"""
from django.conf import settings
from django.core.cache import cache
from django.db import connection
import logging

logger = logging.getLogger(__name__)

def setup_monitoring():
    """Initialize application monitoring."""
    if not settings.DEBUG:
        # Setup database connection monitoring
        setup_db_monitoring()
        
        # Setup cache monitoring
        setup_cache_monitoring()
        
        # Setup request monitoring
        setup_request_monitoring()

def setup_db_monitoring():
    """Setup database connection monitoring."""
    try:
        from django.db.backends.signals import connection_created
        
        def callback(sender, connection, **kwargs):
            logger.info(f"New database connection created: {connection.alias}")
        
        connection_created.connect(callback)
        logger.info("Database monitoring initialized")
    except Exception as e:
        logger.error(f"Failed to setup database monitoring: {e}")

def setup_cache_monitoring():
    """Setup cache monitoring."""
    try:
        # Test cache connection
        cache.set('monitoring_test', True, 10)
        assert cache.get('monitoring_test') is True
        cache.delete('monitoring_test')
        logger.info("Cache monitoring initialized")
    except Exception as e:
        logger.error(f"Failed to setup cache monitoring: {e}")

def setup_request_monitoring():
    """Setup request monitoring."""
    try:
        from django.core.signals import request_started, request_finished
        
        def started_callback(sender, environ, **kwargs):
            logger.info(f"Request started: {environ.get('PATH_INFO')}")
        
        def finished_callback(sender, **kwargs):
            logger.info("Request finished")
        
        request_started.connect(started_callback)
        request_finished.connect(finished_callback)
        logger.info("Request monitoring initialized")
    except Exception as e:
        logger.error(f"Failed to setup request monitoring: {e}")
