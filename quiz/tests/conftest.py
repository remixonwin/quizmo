"""
Test fixtures and configuration.
"""
import json
import os

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client

def load_fixture(filename):
    """Load fixture data from a JSON file."""
    fixture_path = os.path.join(settings.TEST_FIXTURE_PATH, filename)
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture
def test_users_fixture():
    """Load test users fixture data."""
    return load_fixture('test_users.json')

@pytest.fixture
def help_page_fixture():
    """Load help page fixture data."""
    return load_fixture('help_page.json')['help_page']

@pytest.fixture
def authenticated_client():
    """Create an authenticated test client."""
    client = Client()
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    client.login(username='testuser', password='testpass123')
    return client
