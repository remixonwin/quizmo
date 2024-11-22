"""
Authentication settings for the quiz application.
"""

# Login settings
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutes
ACCOUNT_LOCKOUT_DURATION = 900  # 15 minutes
RATE_LIMIT_ATTEMPTS = 5  # Maximum attempts before rate limiting kicks in

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [
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
]

# Email settings
EMAIL_VERIFICATION_REQUIRED = True
EMAIL_VERIFICATION_TIMEOUT = 86400  # 24 hours
EMAIL_VERIFICATION_TOKEN_LENGTH = 32

# Email domain blacklist
BLACKLISTED_EMAIL_DOMAINS = [
    'example.com',
    'test.com',
    'invalid.com',
]

# Messages
LOGIN_ERROR_MESSAGE = 'Invalid username or password.'
EMAIL_VERIFICATION_REQUIRED_MESSAGE = 'Please verify your email address to login.'
ACCOUNT_LOCKED_MESSAGE = 'Account locked. Please try again later.'
INVALID_TOKEN_MESSAGE = 'Invalid verification link. Please try again.'
EMAIL_NOT_REGISTERED_MESSAGE = 'Email not registered.'
REGISTRATION_SUCCESS_MESSAGE = 'Registration successful! Please check your email to verify your account.'
PASSWORD_RESET_SENT_MESSAGE = 'Password reset instructions have been sent to your email.'
PASSWORD_RESET_SUCCESS_MESSAGE = 'Your password has been successfully reset.'
PASSWORD_RESET_INVALID_TOKEN_MESSAGE = 'Invalid password reset link. Please try again.'

# Password Reset Settings
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour
PASSWORD_RESET_TOKEN_LENGTH = 32
