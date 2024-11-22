"""
Django test settings.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'test-key-not-for-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'quiz.apps.QuizConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quiz.tests.test_urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'quiz', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Email settings for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Authentication settings
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 300  # 5 minutes
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour
ACCOUNT_LOCKOUT_DURATION = 300  # 5 minutes
BLACKLISTED_EMAIL_DOMAINS = ['example.com', 'test.com']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'quiz.validators.UppercaseValidator',
    },
    {
        'NAME': 'quiz.validators.LowercaseValidator',
    },
    {
        'NAME': 'quiz.validators.DigitValidator',
    },
    {
        'NAME': 'quiz.validators.SpecialCharacterValidator',
    },
]

# Custom messages
LOGIN_ERROR_MESSAGE = 'Invalid username or password'
ACCOUNT_LOCKED_MESSAGE = 'Too many login attempts. Please try again later.'
PASSWORD_MISMATCH_MESSAGE = 'The two password fields did not match.'
USERNAME_EXISTS_MESSAGE = 'This username already exists'
EMAIL_NOT_REGISTERED_MESSAGE = 'This email address is not registered'
COMMON_PASSWORD_MESSAGE = 'This password is too common'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'quiz', 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms Settings
CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'

# Contact Information
CONTACT_EMAIL = 'support@example.com'
SUPPORT_PHONE = '+1-555-123-4567'

# Minnesota DMV Manual URL
MN_DRIVERS_MANUAL_URL = 'https://dps.mn.gov/divisions/dvs/forms-documents/Documents/Minnesota_Drivers_Manual.pdf'

# Help content configuration
HELP_QUICK_START = [
    {
        'title': 'Creating an Account',
        'description': 'Register with your email to start practicing.'
    },
    {
        'title': 'Taking a Quiz',
        'description': 'Select a quiz and answer the questions.'
    }
]

HELP_STUDY_MATERIALS = [
    {
        'title': 'Study Guides',
        'description': 'Comprehensive study materials for each quiz topic.'
    },
    {
        'title': 'Practice Questions',
        'description': 'Sample questions to help you prepare for quizzes.'
    }
]

HELP_STUDY_TIPS = [
    {
        'title': 'Review Regularly',
        'description': 'Set aside time each day to practice.'
    },
    {
        'title': 'Track Progress',
        'description': 'Monitor your scores to identify areas for improvement.'
    }
]

HELP_FAQS = [
    {
        'category': 'General',
        'questions': [
            {
                'question': 'How many questions are in each quiz?',
                'answer': 'Each quiz typically contains 20-25 questions.'
            },
            {
                'question': 'How much time do I have?',
                'answer': 'Most quizzes have a 30-minute time limit.'
            }
        ]
    },
    {
        'category': 'Scoring',
        'questions': [
            {
                'question': 'What is the passing score?',
                'answer': 'You need to score 80% or higher to pass.'
            },
            {
                'question': 'Can I retake a quiz?',
                'answer': 'Yes, you can retake quizzes as many times as you want.'
            }
        ]
    }
]

HELP_CONTACT_INFO = {
    'email': 'support@example.com',
    'phone': '1-800-555-0123',
    'hours': 'Monday to Friday, 9 AM to 5 PM',
    'support_url': '/help/contact'
}

# Cache settings
CACHE_TIMEOUT = 300  # 5 minutes
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Test Settings
from django.test.runner import DiscoverRunner

class QuizTestRunner(DiscoverRunner):
    """Custom test runner for the quiz app."""
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
