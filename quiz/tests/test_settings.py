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
        'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

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

# Help Page Settings
QUIZ_FAQS = [
    {
        'question': 'What is the Minnesota DMV Practice Test?',
        'answer': 'The Minnesota DMV Practice Test is a web application designed to help you prepare for your driver\'s permit test. It provides practice questions based on the official Minnesota Driver\'s Manual.'
    },
    {
        'question': 'How do I create an account?',
        'answer': 'Click the "Register" button in the top right corner, fill out the registration form with your email and password, and click "Sign Up". You\'ll receive a confirmation email to activate your account.'
    },
    {
        'question': 'How are practice tests scored?',
        'answer': 'Practice tests are scored immediately after completion. You need to score 80% or higher to pass. Each question is worth one point, and you\'ll see detailed explanations for all answers.'
    },
    {
        'question': 'Can I retake practice tests?',
        'answer': 'Yes! You can take practice tests as many times as you want. Each attempt will have randomly selected questions to help you learn all the material.'
    },
    {
        'question': 'How should I prepare for the test?',
        'answer': 'Start by reading the Minnesota Driver\'s Manual, then take our practice tests to assess your knowledge. Review the explanations for any questions you miss and focus on those topics.'
    }
]

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
