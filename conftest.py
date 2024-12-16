
import os
import pytest

@pytest.fixture(scope='session', autouse=True)
def set_django_allow_async_unsafe():
    os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
    yield
    del os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']