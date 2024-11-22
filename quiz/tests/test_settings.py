"""
Test settings for Django test runner.
"""
from quiz.settings.base import *  # noqa

# Use an in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable debug mode
DEBUG = False

# Use a faster password hasher during tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable CSRF protection in tests
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE
    if middleware != 'django.middleware.csrf.CsrfViewMiddleware'
]

# Configure test-specific apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'quiz.apps.QuizConfig',
    'crispy_forms',
    'crispy_bootstrap5',
]

# Configure test-specific middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configure test-specific templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'quiz' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configure test-specific static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'quiz' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configure test-specific media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configure test-specific auth settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Configure test-specific crispy forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Configure test-specific login attempt settings
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutes
ACCOUNT_LOCKOUT_DURATION = 900  # 15 minutes
RATE_LIMIT_ATTEMPTS = 5  # Maximum attempts before rate limiting kicks in
