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
GENERIC_ERROR_MESSAGE = 'An error occurred. Please try again later.'
INVALID_RESET_LINK_MESSAGE = 'The password reset link is invalid or has expired. Please request a new one.'
INVALID_VERIFICATION_LINK_MESSAGE = 'The verification link is invalid or has expired. Please request a new one.'
EMAIL_VERIFIED_MESSAGE = 'Your email has been verified successfully. You can now login.'
BLACKLISTED_DOMAIN_MESSAGE = 'This email domain is not allowed for registration.'
PASSWORD_RESET_EMAIL_SENT_MESSAGE = 'If an account exists with this email, you will receive password reset instructions.'

# Password complexity messages
PASSWORD_MISMATCH_MESSAGE = 'The two password fields do not match.'
PASSWORD_COMPLEXITY_MESSAGE = 'Password must contain at least one uppercase letter, one number, and be at least 8 characters long.'
PASSWORD_RESET_LINK_EXPIRED_MESSAGE = 'Password reset link has expired. Please request a new one.'
PASSWORD_RESET_LINK_INVALID_MESSAGE = 'Invalid password reset link. Please request a new one.'
EMAIL_EXISTS_MESSAGE = 'This email address is already registered.'
USERNAME_EXISTS_MESSAGE = 'This username is already taken.'
EMAIL_DOMAIN_ERROR_MESSAGE = 'Please use a valid email domain.'

# Password Reset Settings
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour
PASSWORD_RESET_TOKEN_LENGTH = 32
