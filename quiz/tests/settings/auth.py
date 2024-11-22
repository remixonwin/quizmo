"""
Authentication test settings.
"""

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
