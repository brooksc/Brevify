"""
Test frontend UI functionality.
"""
import pytest
import logging
import requests
import time
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_flask_app_running(url, max_retries=5, timeout=2):
    """Check if Flask app is running and accessible."""
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries} to connect to {url}")
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                logger.info(f"Flask app is running and accessible at {url}")
                return True
            logger.warning(f"Flask app returned unexpected status code {response.status_code}")
        except requests.ConnectionError as e:
            logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {str(e)}")
        except requests.Timeout as e:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error checking Flask app: {str(e)}")
        
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 2  # Exponential backoff
            logger.debug(f"Waiting {wait_time} seconds before retry")
            time.sleep(wait_time)
    
    logger.error(f"Could not connect to Flask app at {url} after {max_retries} attempts")
    return False

@pytest.fixture(autouse=True)
def check_app_running(base_url):
    """Ensure Flask app is running before each test."""
    logger.info(f"Checking if Flask app is running at {base_url}")
    assert check_flask_app_running(base_url), "Flask app must be running for tests"

def test_url_input_validation(page, base_url):
    """Test URL input validation."""
    logger.info("Starting URL input validation test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Test URL input field
        logger.debug("Waiting for URL input field")
        url_input = page.locator("#url-input")
        expect(url_input).to_be_visible()
        logger.debug("URL input field is visible")

        # Test invalid URL
        logger.debug("Filling invalid URL")
        url_input.fill("invalid-url")
        logger.debug("Waiting for submit button")
        submit_button = page.locator("#submit-button")
        expect(submit_button).to_be_visible()
        logger.debug("Submit button is visible")
        submit_button.click()
        logger.debug("Clicking submit button")

        # Check error message
        logger.debug("Waiting for error message")
        error_message = page.locator("#error-message")
        expect(error_message).to_be_visible()
        logger.info("Error message appeared as expected")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="url_validation_failure.png")
        raise

def test_loading_states(page, base_url):
    """Test loading states and indicators."""
    logger.info("Starting loading states test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Fill valid URL
        logger.debug("Filling valid URL")
        url_input = page.locator("#url-input")
        url_input.fill("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        # Click submit and check loading state
        logger.debug("Waiting for submit button")
        submit_button = page.locator("#submit-button")
        expect(submit_button).to_be_visible()
        logger.debug("Submit button is visible")
        submit_button.click()
        logger.debug("Clicking submit button")

        # Check loading spinner
        logger.debug("Waiting for loading spinner")
        loading_spinner = page.locator("#loading-spinner")
        expect(loading_spinner).to_be_visible()
        logger.info("Loading spinner appeared as expected")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="loading_states_failure.png")
        raise

def test_ai_service_button(page, base_url):
    """Test AI service button functionality."""
    logger.info("Starting AI service button test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Check initial state
        logger.debug("Checking initial state of AI button")
        ai_button = page.locator("#ai-service-button")
        expect(ai_button).to_be_visible()

        # Click button and check response area
        logger.debug("Clicking AI button")
        ai_button.click()

        # Check response area
        logger.debug("Waiting for response area")
        response_area = page.locator("#ai-response")
        expect(response_area).to_be_visible()
        logger.info("Response area appeared as expected")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="ai_button_failure.png")
        raise

def test_local_storage(page, base_url):
    """Test local storage functionality."""
    logger.info("Starting local storage test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Set test data in localStorage
        logger.debug("Setting test data in local storage")
        page.evaluate("localStorage.setItem('lastUrl', 'https://www.youtube.com/watch?v=test123')")

        # Refresh page and check persistence
        logger.debug("Refreshing page")
        page.reload()
        logger.debug("Page reloaded successfully")

        # Check if URL was restored
        logger.debug("Checking stored URL")
        stored_url = page.evaluate("document.getElementById('url-input').value")
        assert stored_url == "https://www.youtube.com/watch?v=test123"
        logger.info("Local storage test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="local_storage_failure.png")
        raise

def test_error_handling(page, base_url):
    """Test error handling and display."""
    logger.info("Starting error handling test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Simulate network error
        logger.debug("Simulating network error")
        page.route("**/api/transcribe**", lambda route: route.abort())

        # Fill valid URL and submit
        logger.debug("Filling valid URL")
        url_input = page.locator("#url-input")
        url_input.fill("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        # Click submit and check error
        logger.debug("Waiting for submit button")
        submit_button = page.locator("#submit-button")
        expect(submit_button).to_be_visible()
        logger.debug("Submit button is visible")
        submit_button.click()
        logger.debug("Clicking submit button")

        # Check error message
        logger.debug("Waiting for error message")
        error_message = page.locator("#error-message")
        expect(error_message).to_be_visible()
        logger.info("Error message appeared as expected")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="error_handling_failure.png")
        raise

def test_theme_settings(page, base_url):
    """Test theme settings functionality."""
    logger.info("Starting theme settings test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Open settings panel
        logger.debug("Opening settings panel")
        settings_button = page.locator("#settings-button")
        settings_button.click()
        settings_panel = page.locator("#settings-panel")
        expect(settings_panel).to_be_visible()

        # Test initial auto theme
        logger.debug("Checking initial theme")
        theme_select = page.locator("#theme-select")
        expect(theme_select).to_have_value("auto")

        # Test dark theme
        logger.debug("Testing dark theme")
        theme_select.select_option("dark")
        assert page.evaluate("document.documentElement.classList.contains('dark')") == True, "Dark theme not applied"
        assert page.evaluate("localStorage.getItem('theme')") == "dark", "Theme not saved to localStorage"

        # Test light theme
        logger.debug("Testing light theme")
        theme_select.select_option("light")
        assert page.evaluate("document.documentElement.classList.contains('dark')") == False, "Dark theme still applied"
        assert page.evaluate("localStorage.getItem('theme')") == "light", "Theme not saved to localStorage"

        # Test auto theme
        logger.debug("Testing auto theme")
        theme_select.select_option("auto")
        assert page.evaluate("localStorage.getItem('theme')") == "auto", "Theme not saved to localStorage"

        # Refresh page and check persistence
        logger.debug("Testing theme persistence")
        page.reload()
        theme_select = page.locator("#theme-select")
        expect(theme_select).to_have_value("auto")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="theme_test_failure.png")
        raise

def test_keyboard_navigation(page, base_url):
    """Test keyboard navigation and accessibility."""
    logger.info("Starting keyboard navigation test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Test tab order
        logger.debug("Testing tab order")
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "settings-button", "First tab should focus settings button"
        
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "url-input", "Second tab should focus URL input"
        
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "submit-button", "Third tab should focus submit button"
        
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "ai-service-button", "Fourth tab should focus AI button"

        # Test settings panel keyboard interaction
        logger.debug("Testing settings panel keyboard interaction")
        # Go back to settings button
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Shift+Tab")
        assert page.evaluate("document.activeElement.id") == "settings-button", "Should focus settings button"
        
        page.keyboard.press("Enter")
        settings_panel = page.locator("#settings-panel")
        expect(settings_panel).to_be_visible()
        
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "close-settings", "Tab should focus close button"
        
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "theme-select", "Tab should focus theme select"
        
        # Test escape key
        logger.debug("Testing escape key")
        page.keyboard.press("Escape")
        expect(settings_panel).to_be_hidden()

        logger.info("Keyboard navigation test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="keyboard_nav_failure.png")
        raise

def test_aria_labels(page, base_url):
    """Test ARIA labels and roles."""
    logger.info("Starting ARIA labels test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Test URL input ARIA
        url_input = page.locator("#url-input")
        expect(url_input).to_have_attribute("aria-label", "YouTube URL input")

        # Test submit button ARIA
        submit_button = page.locator("#submit-button")
        expect(submit_button).to_have_attribute("aria-label", "Analyze URL")

        # Test settings button ARIA
        settings_button = page.locator("#settings-button")
        expect(settings_button).to_have_attribute("aria-label", "Open settings")
        expect(settings_button).to_have_attribute("aria-expanded", "false")

        # Test settings panel ARIA
        settings_panel = page.locator("#settings-panel")
        expect(settings_panel).to_have_attribute("role", "dialog")
        expect(settings_panel).to_have_attribute("aria-labelledby", "settings-title")

        # Test theme select ARIA
        theme_select = page.locator("#theme-select")
        expect(theme_select).to_have_attribute("aria-label", "Select theme")

        # Test loading spinner ARIA
        loading_spinner = page.locator("#loading-spinner")
        expect(loading_spinner).to_have_attribute("role", "status")
        expect(loading_spinner).to_have_attribute("aria-live", "polite")

        # Test error message ARIA
        error_message = page.locator("#error-message")
        expect(error_message).to_have_attribute("role", "alert")
        expect(error_message).to_have_attribute("aria-live", "polite")

        logger.info("ARIA labels test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="aria_labels_failure.png")
        raise

def test_dark_mode_backgrounds(page, base_url):
    """Test dark mode to ensure no white backgrounds."""
    logger.info("Starting dark mode background test")
    try:
        logger.debug(f"Attempting to navigate to {base_url}")
        page.goto(base_url, wait_until="networkidle")
        logger.debug("Page loaded successfully")

        # Open settings and switch to dark mode
        logger.debug("Opening settings panel")
        settings_button = page.locator("#settings-button")
        settings_button.click()
        
        logger.debug("Switching to dark mode")
        theme_select = page.locator("#theme-select")
        theme_select.select_option("dark")
        
        # Wait for dark mode transition
        page.wait_for_timeout(1000)  # Wait for any CSS transitions

        # Check all elements for background colors
        logger.debug("Checking background colors")
        elements_with_bg = page.evaluate("""() => {
            const elements = document.querySelectorAll('*');
            const whiteBgElements = [];
            
            elements.forEach(el => {
                const style = window.getComputedStyle(el);
                const bgColor = style.backgroundColor;
                if (bgColor === 'rgb(255, 255, 255)' || bgColor === '#ffffff' || bgColor === 'white') {
                    whiteBgElements.push({
                        id: el.id,
                        class: el.className,
                        tag: el.tagName.toLowerCase(),
                        bgColor: bgColor
                    });
                }
            });
            
            return whiteBgElements;
        }""")

        # Assert no white backgrounds
        assert len(elements_with_bg) == 0, f"Found elements with white background in dark mode: {elements_with_bg}"
        
        # Check body background is dark
        body_bg = page.evaluate("""() => {
            const style = window.getComputedStyle(document.body);
            return style.backgroundColor;
        }""")
        
        # Convert rgb color to brightness value (0-255)
        def get_brightness(rgb_str):
            # Extract RGB values from string like 'rgb(r, g, b)'
            r, g, b = map(int, rgb_str.strip('rgb()').split(','))
            # Calculate perceived brightness using standard formula
            return (r * 299 + g * 587 + b * 114) / 1000

        body_brightness = get_brightness(body_bg)
        assert body_brightness < 128, f"Body background is too bright in dark mode: {body_bg}"

        logger.info("Dark mode background test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        page.screenshot(path="dark_mode_failure.png")
        raise
