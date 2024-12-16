# Project Documentation
Generated at Mon Dec 16 07:37:28 UTC 2024

## Project Structure
```
.
├── .devcontainer
│   ├── devcontainer.json
│   └── icon.svg
├── .git
│   ├── FETCH_HEAD
│   ├── HEAD
│   ├── branches
│   ├── config
│   ├── description
│   ├── hooks
│   │   ├── applypatch-msg.sample
│   │   ├── commit-msg.sample
│   │   ├── fsmonitor-watchman.sample
│   │   ├── post-update.sample
│   │   ├── pre-applypatch.sample
│   │   ├── pre-commit.sample
│   │   ├── pre-merge-commit.sample
│   │   ├── pre-push.sample
│   │   ├── pre-rebase.sample
│   │   ├── pre-receive.sample
│   │   ├── prepare-commit-msg.sample
│   │   ├── push-to-checkout.sample
│   │   ├── sendemail-validate.sample
│   │   └── update.sample
│   ├── index
│   ├── info
│   │   └── exclude
│   ├── logs
│   │   ├── HEAD
│   │   └── refs
│   │       ├── heads
│   │       │   └── main
│   │       └── remotes
│   │           └── origin
│   │               └── HEAD
│   ├── objects
│   │   ├── info
│   │   └── pack
│   │       ├── pack-af16bd7ad7ad932f210077bf0b71ff1ffc7ffd5d.idx
│   │       ├── pack-af16bd7ad7ad932f210077bf0b71ff1ffc7ffd5d.pack
│   │       └── pack-af16bd7ad7ad932f210077bf0b71ff1ffc7ffd5d.rev
│   ├── packed-refs
│   ├── refs
│   │   ├── heads
│   │   │   └── main
│   │   ├── remotes
│   │   │   └── origin
│   │   │       └── HEAD
│   │   └── tags
│   └── shallow
├── .gitattributes
├── .gitignore
├── .pytest_cache
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   └── v
│       └── cache
│           ├── lastfailed
│           ├── nodeids
│           └── stepwise
├── .streamlit
│   └── auth.json
├── README.md
├── __pycache__
│   └── conftest.cpython-312-pytest-7.4.4.pyc
├── backend
│   ├── __pycache__
│   │   ├── settings.cpython-312.pyc
│   │   ├── urls.cpython-312.pyc
│   │   └── wsgi.cpython-312.pyc
│   ├── asgi.py
│   ├── core
│   │   ├── __pycache__
│   │   │   ├── admin.cpython-312.pyc
│   │   │   ├── apps.cpython-312.pyc
│   │   │   └── signals.cpython-312.pyc
│   │   ├── admin.py
│   │   ├── api
│   │   │   ├── serializers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   ├── auth.cpython-312.pyc
│   │   │   │   │   └── quiz.cpython-312.pyc
│   │   │   │   ├── auth.py
│   │   │   │   └── quiz.py
│   │   │   └── views
│   │   │       ├── __init__.py
│   │   │       ├── __pycache__
│   │   │       │   ├── __init__.cpython-312.pyc
│   │   │       │   ├── auth.cpython-312.pyc
│   │   │       │   └── quiz.cpython-312.pyc
│   │   │       ├── auth.py
│   │   │       └── quiz.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       ├── 0001_initial.cpython-312.pyc
│   │   │       └── __init__.cpython-312.pyc
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── auth.cpython-312.pyc
│   │   │   │   └── quiz.cpython-312.pyc
│   │   │   ├── auth.py
│   │   │   └── quiz.py
│   │   ├── quiz
│   │   │   └── __init__.py
│   │   ├── signals.py
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-312.pyc
│   │   │   ├── base.py
│   │   │   └── test_cases
│   │   │       ├── __init__.py
│   │   │       ├── __pycache__
│   │   │       │   ├── __init__.cpython-312.pyc
│   │   │       │   ├── test_auth.cpython-312-pytest-7.4.4.pyc
│   │   │       │   ├── test_auth.cpython-312.pyc
│   │   │       │   ├── test_quiz.cpython-312-pytest-7.4.4.pyc
│   │   │       │   └── test_quiz.cpython-312.pyc
│   │   │       ├── test_auth.py
│   │   │       └── test_quiz.py
│   │   ├── utils
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   └── decorators.cpython-312.pyc
│   │   │   └── decorators.py
│   │   └── views
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │   ├── __init__.cpython-312.pyc
│   │       │   ├── auth.cpython-312.pyc
│   │       │   └── quiz.cpython-312.pyc
│   │       ├── auth.py
│   │       ├── quiz.py
│   │       └── utils.py
│   ├── settings.py
│   ├── static
│   │   └── .gitkeep
│   ├── templates
│   │   ├── .gitkeep
│   │   └── index.html
│   ├── urls.py
│   └── wsgi.py
├── codebase.md
├── conftest.py
├── db.sqlite3
├── frontend
│   ├── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-312.pyc
│   ├── base
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       └── __init__.cpython-312.pyc
│   ├── components
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── auth.cpython-312.pyc
│   │   ├── auth.py
│   │   ├── base
│   │   │   ├── __pycache__
│   │   │   │   └── form.cpython-312.pyc
│   │   │   └── form.py
│   │   ├── quiz
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   └── quiz.cpython-312.pyc
│   │   │   └── quiz.py
│   │   └── registry.py
│   ├── main.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── api.cpython-312.pyc
│   │   │   ├── auth.cpython-312.pyc
│   │   │   └── factory.cpython-312.pyc
│   │   ├── api.py
│   │   ├── auth.py
│   │   ├── factory.py
│   │   └── quiz.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── conftest.cpython-312-pytest-7.4.4.pyc
│   │   ├── conftest.py
│   │   ├── e2e
│   │   │   ├── __pycache__
│   │   │   │   └── test_quiz_flow.cpython-312-pytest-7.4.4.pyc
│   │   │   └── test_quiz_flow.py
│   │   ├── integration
│   │   │   ├── __pycache__
│   │   │   │   ├── test_api.cpython-312-pytest-7.4.4.pyc
│   │   │   │   └── test_integration.cpython-312-pytest-7.4.4.pyc
│   │   │   ├── test_api.py
│   │   │   └── test_integration.py
│   │   └── unit
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │   ├── __init__.cpython-312.pyc
│   │       │   ├── test_auth.cpython-312-pytest-7.4.4.pyc
│   │       │   ├── test_base_form.cpython-312-pytest-7.4.4.pyc
│   │       │   ├── test_factory.cpython-312-pytest-7.4.4.pyc
│   │       │   ├── test_forms.cpython-312-pytest-7.4.4.pyc
│   │       │   ├── test_playwright.cpython-312-pytest-7.4.4.pyc
│   │       │   ├── test_quiz.cpython-312-pytest-7.4.4.pyc
│   │       │   ├── test_session.cpython-312-pytest-7.4.4.pyc
│   │       │   └── test_session.cpython-312.pyc
│   │       ├── test_auth.py
│   │       ├── test_base_form.py
│   │       ├── test_factory.py
│   │       ├── test_forms.py
│   │       ├── test_playwright.py
│   │       ├── test_quiz.py
│   │       └── test_session.py
│   └── utils
│       ├── __pycache__
│       │   └── session.cpython-312.pyc
│       ├── session.py
│       └── state.py
├── manage.py
├── pytest.ini
└── requirements.txt

69 directories, 165 files
```

## Configuration Files

### .env.example
```example
SECRET_KEY=my_secret_key
DEBUG=True

# ALLOWED_HOSTS=yourdomain.com,anotherdomain.com (Each host is separated by a comma)
ALLOWED_HOSTS=*

DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=""
DB_USERNAME=""
DB_PASSWORD=""
```

## Source Code

### conftest.py
```py

import os
import pytest

@pytest.fixture(scope='session', autouse=True)
def set_django_allow_async_unsafe():
    os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
    yield
    del os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']```

### backend/wsgi.py
```py
"""
WSGI config for hello_world project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hello_world.settings")

application = get_wsgi_application()
```

### backend/core/apps.py
```py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.core'
    label = 'core'

    def ready(self):
        try:
            import backend.core.signals  # Using absolute import
        except ImportError:
            pass```

### backend/core/views/__init__.py
```py
from .quiz import QuizViewSet
from .auth import (
    RegisterView, ValidateTokenView, PasswordResetView, 
    ResetPasswordView, CustomAuthToken, index
)

__all__ = [
    'index',
    'RegisterView', 
    'ValidateTokenView', 
    'PasswordResetView', 
    'ResetPasswordView',
    'CustomAuthToken', 
    'QuizViewSet'
]```

### backend/core/views/utils.py
```py
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

User = get_user_model()

def retry_on_error(retries=3, delay=1):
    """Decorator to retry a function on failure with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries - 1:
                        raise
                    time.sleep(delay * (2 ** i))
        return wrapper
    return decorator

def atomic_transaction():
    """Decorator to wrap a view method in a database transaction"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_exceptions(func):
    """Decorator to handle common API exceptions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ObjectDoesNotExist as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Internal server error', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

def flush_duplicate_users():
    """Utility function to clean up duplicate user accounts"""
    with transaction.atomic():
        for user in User.objects.all():
            duplicates = User.objects.filter(
                email=user.email
            ).exclude(id=user.id)
            if duplicates.exists():
                # Keep the most recently active user
                latest_user = duplicates.order_by('-last_login').first()
                duplicates.exclude(id=latest_user.id).delete()
    return True

def validate_request_data(required_fields):
    """Decorator to validate required fields in request data"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            missing_fields = [
                field for field in required_fields 
                if field not in request.data
            ]
            if missing_fields:
                return Response(
                    {
                        'error': 'Missing required fields',
                        'fields': missing_fields
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator```

### backend/core/views/quiz.py
```py
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from backend.core.api.serializers.quiz import QuizSerializer, QuestionSerializer
from backend.core.models import Quiz
from backend.core.utils.decorators import retry_on_error

@method_decorator(cache_page(60), name='list')
@method_decorator(retry_on_error(retries=3), name='create')
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        quiz = self.get_object()
        # Add submission logic here
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response(
                e.detail,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response(
                {'error': 'Validation failed', 'details': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='questions')
    def add_question(self, request, pk=None):
        quiz = self.get_object()
        question_data = request.data.copy()
        question_data['quiz'] = quiz.id

        serializer = QuestionSerializer(data=question_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)```

### backend/core/views/auth.py
```py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token  # Add this import
from backend.core.api.serializers.auth import RegisterSerializer, UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken

User = get_user_model()

def index(request):
    """Basic index view"""
    return render(request, 'index.html')

class RegisterView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateTokenView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token_obj = Token.objects.get(key=token)
            return Response({'valid': True, 'user': UserSerializer(token_obj.user).data}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'valid': False}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetView(APIView):
    permission_classes = []
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            # Add password reset logic here
            return Response({'message': 'Reset email sent'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class ResetPasswordView(APIView):
    permission_classes = []
    def post(self, request):
        # Add password reset confirmation logic here
        return Response({'message': 'Password reset'})

class CustomAuthToken(ObtainAuthToken):
    """Custom token-based authentication view"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})```

### backend/core/models/__init__.py
```py
from .auth import User
from .quiz import Quiz, Question, Choice

default_app_config = 'backend.core.apps.CoreConfig'

__all__ = ['User', 'Quiz', 'Question', 'Choice']```

### backend/core/models/quiz.py
```py
from django.db import models
from django.conf import settings

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.CharField(max_length=500)
    points = models.IntegerField(default=1)

class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
```

### backend/core/models/auth.py
```py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model for the application."""
    
    # Custom fields
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Required for custom user model
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        app_label = 'core'  # Add this to explicitly set the app label

    def __str__(self):
        return self.username```

### backend/core/utils/__init__.py
```py
from .decorators import retry_on_error, atomic_transaction, handle_exceptions, validate_request_data
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    return response

__all__ = [
    'retry_on_error',
    'atomic_transaction',
    'handle_exceptions',
    'validate_request_data',
    'custom_exception_handler'
]```

### backend/core/utils/decorators.py
```py
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import time

def retry_on_error(retries=3, delay=1):
    """Decorator to retry a function on failure with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries - 1:
                        raise
                    time.sleep(delay * (2 ** i))
        return wrapper
    return decorator

def atomic_transaction():
    """Decorator to wrap a view method in a database transaction"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_exceptions(func):
    """Decorator to handle common API exceptions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ObjectDoesNotExist as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Internal server error', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

def validate_request_data(required_fields):
    """Decorator to validate required fields in request data"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            missing_fields = [
                field for field in required_fields 
                if field not in request.data
            ]
            if missing_fields:
                return Response(
                    {
                        'error': 'Missing required fields',
                        'fields': missing_fields
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator

__all__ = [
    'retry_on_error',
    'atomic_transaction', 
    'handle_exceptions',
    'validate_request_data'
]```

### backend/core/admin.py
```py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.authtoken.models import Token
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Customize the admin interface for the User model if needed
    pass

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', 'created']
    search_fields = ['key', 'user__username', 'user__email']

# ...existing admin registrations...```

### backend/core/migrations/__init__.py
```py
```

### backend/core/migrations/0001_initial.py
```py
# Generated by Django 5.0.10 on 2024-12-16 04:29

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=500)),
                ("points", models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("bio", models.TextField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Choice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=255)),
                ("is_correct", models.BooleanField(default=False)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="choices",
                        to="core.question",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Quiz",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quizzes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="question",
            name="quiz",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="core.quiz",
            ),
        ),
    ]
```

### backend/core/quiz/__init__.py
```py

from .models import Quiz, Question, Choice
from .views import QuizViewSet
from .serializers import QuizSerializer, QuestionSerializer, ChoiceSerializer

__all__ = [
    'Quiz', 'Question', 'Choice',
    'QuizViewSet',
    'QuizSerializer', 'QuestionSerializer', 'ChoiceSerializer'
]```

### backend/core/api/views/__init__.py
```py
from .auth import RegisterView, ValidateTokenView, PasswordResetView, ResetPasswordView, CustomAuthToken
from .quiz import QuizViewSet

__all__ = [
    'RegisterView', 'ValidateTokenView', 'PasswordResetView', 'ResetPasswordView', 
    'CustomAuthToken', 'QuizViewSet'
]```

### backend/core/api/views/quiz.py
```py
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action  # Add this import
from backend.core.models import Quiz
from ..serializers.quiz import QuizSerializer, QuestionSerializer

class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quizzes"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        if 'author' in request.data:
            return Response(
                {'author': 'Author cannot be changed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], url_path='questions')
    def add_question(self, request, pk=None):
        quiz = self.get_object()
        question_data = request.data.copy()
        question_data['quiz'] = quiz.id
    
        serializer = QuestionSerializer(data=question_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)```

### backend/core/api/views/auth.py
```py
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ..serializers import UserSerializer, RegisterSerializer

User = get_user_model()

class CustomAuthToken(ObtainAuthToken):
    """Custom token-based authentication view"""
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class RegisterView(APIView):
    """User registration view"""
    
    permission_classes = []
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateTokenView(APIView):
    """Token validation view"""
    
    permission_classes = []  # Allow any user to access this view

    def post(self, request):
        token_key = request.data.get('token')
        if not token_key:
            return Response({'valid': False, 'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = Token.objects.get(key=token_key)
            return Response({'valid': True, 'user_id': token.user_id}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'valid': False, 'error': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)

class PasswordResetView(APIView):
    """Password reset request view"""
    
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            # Add password reset logic here
            return Response({'message': 'Password reset email sent'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class ResetPasswordView(APIView):
    """Password reset confirmation view"""
    
    permission_classes = []
    
    def post(self, request):
        # Add password reset confirmation logic here
        return Response({'message': 'Password reset successful'})```

### backend/core/api/serializers/__init__.py
```py
from .auth import UserSerializer, RegisterSerializer
from .quiz import QuizSerializer, QuestionSerializer, ChoiceSerializer

__all__ = ['UserSerializer', 'RegisterSerializer', 'QuizSerializer', 'QuestionSerializer', 'ChoiceSerializer']```

### backend/core/api/serializers/quiz.py
```py
from rest_framework import serializers
from backend.core.models import Quiz, Question, Choice

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'points', 'choices', 'quiz']

    def validate_choices(self, value):
        """
        Check that at least two choices are provided
        """
        if len(value) < 2:
            raise serializers.ValidationError("At least two choices are required")
        return value

    def validate_points(self, value):
        """
        Check that points are non-negative
        """
        if value < 0:
            raise serializers.ValidationError("Points must be non-negative")
        return value

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        if not choices_data:
            raise serializers.ValidationError({"choices": "At least two choices are required"})
            
        question = Question.objects.create(**validated_data)
        
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        return question

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'questions']

    def validate_questions(self, value):
        """
        Check that at least one question is provided and each question has valid choices
        """
        if not value:
            raise serializers.ValidationError("At least one question is required")
        
        for question in value:
            choices = question.get('choices', [])
            if len(choices) < 2:
                raise serializers.ValidationError("Each question must have at least two choices")
            if not any(choice.get('is_correct', False) for choice in choices):
                raise serializers.ValidationError("Each question must have at least one correct answer")
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(quiz=quiz, **question_data)
            
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        return quiz

    def update(self, instance, validated_data):
        if 'questions' in validated_data:
            questions_data = validated_data.pop('questions')
            instance.questions.all().delete()  # Remove existing questions
            
            for question_data in questions_data:
                choices_data = question_data.pop('choices')
                question = Question.objects.create(quiz=instance, **question_data)
                
                for choice_data in choices_data:
                    Choice.objects.create(question=question, **choice_data)

        return super().update(instance, validated_data)```

### backend/core/api/serializers/auth.py
```py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')```

### backend/core/signals.py
```py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User  # Direct import from models

@receiver(pre_save, sender=User)
def clean_email(sender, instance, **kwargs):
    """Clean and validate the user's email before saving."""
    if instance.email:
        instance.email = instance.email.lower()```

### backend/core/tests/__init__.py
```py
