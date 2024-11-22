import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import logging
import os
import shutil
import tempfile
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

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

@pytest.fixture(scope="function")
def selenium_driver():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create a temporary directory for Firefox profile
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Configure Firefox options
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.set_preference('browser.cache.disk.enable', False)
        options.set_preference('browser.cache.memory.enable', False)
        options.set_preference('browser.cache.offline.enable', False)
        options.set_preference('network.http.use-cache', False)
        
        # Configure Firefox service with explicit port and logging
        service = Service(
            GeckoDriverManager().install(),
            port=2828,
            log_path='/tmp/geckodriver.log'
        )
        
        # Initialize the driver with configured options
        driver = webdriver.Firefox(
            service=service,
            options=options
        )
        
        # Set timeouts
        driver.implicitly_wait(20)
        driver.set_page_load_timeout(30)
        
        logger.info("WebDriver initialized successfully")
        yield driver
        
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {str(e)}")
        raise
        
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")
            
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory: {str(e)}")
