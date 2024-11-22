import os
from datetime import datetime

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Define log file paths
AUTH_LOG_FILE = os.path.join(LOGS_DIR, 'auth.log')
ERROR_LOG_FILE = os.path.join(LOGS_DIR, 'error.log')
SECURITY_LOG_FILE = os.path.join(LOGS_DIR, 'security.log')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        'auth_file': {
            'class': 'logging.FileHandler',
            'filename': AUTH_LOG_FILE,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': ERROR_LOG_FILE,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'security_file': {
            'class': 'logging.FileHandler',
            'filename': SECURITY_LOG_FILE,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'error_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'quiz.auth': {
            'handlers': ['auth_file', 'console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'quiz.security': {
            'handlers': ['security_file', 'console', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
