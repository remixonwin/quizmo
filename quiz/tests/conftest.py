"""
Pytest configuration for quiz tests.
"""
import os
import json
import pytest
from django.conf import settings

# Configure Django settings before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz.tests.test_settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.test import Client

def load_fixture(filename):
    """Load test fixture from JSON file."""
    fixture_path = os.path.join(settings.TEST_FIXTURE_PATH, filename)
    with open(fixture_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def help_page_fixture():
    """Load help page fixture data."""
    return load_fixture('help_page.json')['help_page']

@pytest.fixture
def test_users_fixture():
    """Load test users fixture data."""
    return load_fixture('test_users.json')['test_users']

@pytest.fixture
def test_user(test_users_fixture):
    """Create a test user."""
    user_data = next(user for user in test_users_fixture if user['username'] == settings.TEST_USER['USERNAME'])
    return User.objects.create_user(
        username=user_data['username'],
        password=user_data['password'],
        email=user_data['email'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )

@pytest.fixture
def authenticated_client(test_user):
    """Create an authenticated client."""
    client = Client()
    client.login(
        username=settings.TEST_USER['USERNAME'],
        password=settings.TEST_USER['PASSWORD']
    )
    return client

@pytest.fixture
def help_page_content(help_page_fixture):
    """Return help page content configuration."""
    return {
        'title': help_page_fixture['title'],
        'quick_start': help_page_fixture['quick_start'],
        'study_tips': help_page_fixture['study_tips'],
        'support_email': help_page_fixture['support']['email'],
        'support_phone': help_page_fixture['support']['phone']
    }

@pytest.fixture
def faq_content(help_page_fixture):
    """Return FAQ content for testing."""
    return help_page_fixture['faqs']
