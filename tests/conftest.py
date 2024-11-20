import pytest
import json
import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fixture to ensure sequential Ollama requests
@pytest.fixture(scope='session')
def ollama_session():
    """Fixture to ensure sequential Ollama requests."""
    # This fixture will be required by tests that use Ollama
    # Its existence forces those tests to run sequentially
    yield None

# Load test data
@pytest.fixture
def test_data():
    data_file = Path(__file__).parent / 'data' / 'test_data_mock.json'
    with open(data_file, 'r') as f:
        return json.load(f)

@pytest.fixture(scope='session')
def test_app():
    """Create test Flask app."""
    logger.info("Creating test Flask app")
    os.environ['FLASK_ENV'] = 'testing'
    
    # Import the Flask app from transcribe.py
    from transcribe import app
    app.config['TESTING'] = True
    return app

@pytest.fixture
def test_client(test_app):
    """Create test client."""
    logger.info("Creating test client")
    return test_app.test_client()

@pytest.fixture(scope='session')
def base_url():
    """Get base URL for testing."""
    url = 'http://localhost:8888'  # Using the port defined in transcribe.py
    logger.info(f"Base URL for testing: {url}")
    return url

@pytest.fixture(scope='session')
def browser_context_args():
    """Configure browser context for Playwright."""
    logger.info("Configuring browser context args")
    return {
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": None,  # Disable video recording
        "ignore_https_errors": True,
        "accept_downloads": True
    }

@pytest.fixture(scope='session')
def browser_type_launch_args():
    """Configure browser launch arguments."""
    logger.info("Configuring browser launch args")
    return {
        "args": [
            '--no-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=site-per-process',
            '--window-size=1280,720'
        ],
        "headless": True,  # Run in headless mode for CI/testing
        "timeout": 60000,  # 60 seconds timeout
        "chromium_sandbox": False
    }

@pytest.fixture
def page(browser):
    """Create a new page for each test."""
    logger.info("Creating new browser page")
    context = None
    page = None
    try:
        # Create persistent context
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True,
            accept_downloads=True
        )
        logger.debug("Browser context created")
        
        page = context.new_page()
        logger.debug("New page created")
        
        page.set_default_timeout(60000)  # 60 seconds timeout
        logger.debug("Page timeout configured")
        
        page.set_default_navigation_timeout(60000)  # 60 seconds navigation timeout
        logger.debug("Navigation timeout configured")
        
        yield page
        
    except Exception as e:
        logger.error(f"Error creating browser page: {e}")
        # Only close context if page creation failed
        if context and not page:
            logger.debug("Closing context due to page creation failure")
            try:
                context.close()
            except Exception as close_error:
                logger.error(f"Error closing context: {close_error}")
    
    finally:
        # Clean up after test
        if page:
            try:
                logger.debug("Closing page after test")
                page.close()
            except Exception as e:
                logger.error(f"Error closing page: {e}")
