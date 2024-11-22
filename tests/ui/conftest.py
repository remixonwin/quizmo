import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_chromium_version():
    try:
        result = subprocess.run(['chromium', '--version'], capture_output=True, text=True)
        version = result.stdout.strip().split()[1]  # Format: "Chromium X.Y.Z.W snap"
        return version
    except Exception as e:
        logger.error(f"Failed to get Chromium version: {str(e)}")
        return None

@pytest.fixture(scope="session")
def browser():
    """
    Create a Selenium WebDriver instance for testing.
    """
    chrome_options = Options()
    
    # Enable headless mode
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Set Chrome preferences for stability
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.binary_location = "/snap/bin/chromium"  # Set Chromium binary path
    
    # Set window size
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        logger.info("Initializing Chrome WebDriver...")
        chromium_version = get_chromium_version()
        logger.info(f"Detected Chromium version: {chromium_version}")
        
        # Download matching ChromeDriver if not exists
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
        if not os.path.exists(chromedriver_path):
            logger.info("ChromeDriver not found, downloading...")
            subprocess.run([
                'wget',
                '-O', 'chromedriver_linux64.zip',
                f'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chromium_version}/linux64/chromedriver-linux64.zip'
            ], check=True)
            subprocess.run(['unzip', '-o', 'chromedriver_linux64.zip'], check=True)
            subprocess.run(['mv', 'chromedriver-linux64/chromedriver', './chromedriver'], check=True)
            subprocess.run(['chmod', '+x', 'chromedriver'], check=True)
            subprocess.run(['rm', '-rf', 'chromedriver-linux64', 'chromedriver_linux64.zip'], check=True)
        
        # Initialize the Chrome WebDriver with explicit service
        service = Service(
            executable_path=chromedriver_path,
            log_output=os.path.join(os.getcwd(), "chromedriver.log")
        )
        
        logger.info("Creating Chrome WebDriver instance...")
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        
        logger.info("WebDriver created successfully")
        
        yield driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        if os.path.exists("chromedriver.log"):
            with open("chromedriver.log", "r") as f:
                logger.error("ChromeDriver log:")
                logger.error(f.read())
        raise
    finally:
        try:
            logger.info("Closing WebDriver...")
            driver.quit()
        except Exception as e:
            logger.error(f"Error while closing WebDriver: {str(e)}")

@pytest.fixture
def live_server_url(live_server):
    """
    Get the live server URL for testing.
    """
    return live_server.url
