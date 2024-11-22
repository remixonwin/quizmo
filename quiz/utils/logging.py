"""
Logging utilities for the quiz app.
"""
import logging
import json
import traceback
from functools import wraps
from typing import Any, Dict, Optional
from django.http import HttpRequest
from django.conf import settings
import logging.config
import os

logger = logging.getLogger(__name__)

def setup_logging():
    """Set up logging configuration for the quiz app."""
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(settings.BASE_DIR, 'logs', 'quiz.log'),
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'json',
            },
            'security': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(settings.BASE_DIR, 'logs', 'security.log'),
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'json',
            },
            'performance': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(settings.BASE_DIR, 'logs', 'performance.log'),
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'json',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
            'quiz': {
                'handlers': ['console', 'file'],
                'level': settings.LOGLEVEL,
                'propagate': True,
            },
            'quiz.security': {
                'handlers': ['security', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'quiz.performance': {
                'handlers': ['performance', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'quiz.auth': {
                'handlers': ['security', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(settings.BASE_DIR, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    logging.config.dictConfig(logging_config)
    logger.info("Logging configuration initialized")

def log_error(
    request: HttpRequest,
    error: Exception,
    level: str = 'error',
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """Log an error with request context."""
    log_data = {
        'error_type': error.__class__.__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
        'request_path': request.path,
        'request_method': request.method,
        'user_id': getattr(request.user, 'id', None),
        'ip_address': request.META.get('REMOTE_ADDR'),
    }
    
    if extra:
        log_data.update(extra)
    
    getattr(logger, level)(json.dumps(log_data))

def log_function_call(func):
    """Decorator to log function calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f'Calling {func.__name__} with args={args}, kwargs={kwargs}')
            result = func(*args, **kwargs)
            logger.debug(f'{func.__name__} completed successfully')
            return result
        except Exception as e:
            logger.error(f'Error in {func.__name__}: {str(e)}')
            raise
    return wrapper

def log_model_changes(sender, instance, created, **kwargs):
    """Log model changes."""
    action = 'created' if created else 'updated'
    logger.info(f'{sender.__name__} {instance.id} {action}')

# Set up loggers
auth_logger = logging.getLogger('quiz.auth')
security_logger = logging.getLogger('quiz.security')
performance_logger = logging.getLogger('quiz.performance')
