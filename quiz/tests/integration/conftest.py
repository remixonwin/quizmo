import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def django_client():
    return Client()

@pytest.fixture
def test_user(db):
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    return user

@pytest.fixture
def authenticated_client(django_client, test_user):
    django_client.login(username='testuser', password='testpass123')
    return django_client

@pytest.fixture
def authenticated_api_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client
