import pytest
import base64
from playwright.sync_api import expect
import requests
import json
import os
import time
import fcntl
from pathlib import Path

# Module-level fixture to ensure single execution
@pytest.fixture(scope="module", autouse=True)
def ensure_single_process():
    """Ensure tests in this module run in a single process."""
    yield

def acquire_ollama_lock():
    """Acquire a lock to ensure only one process uses Ollama at a time."""
    lock_file = '/tmp/ollama_test.lock'
    while True:
        try:
            fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except (IOError, OSError):
            time.sleep(1)  # Wait before retrying

def release_ollama_lock(fd):
    """Release the Ollama lock."""
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)

def analyze_with_ollama(image_path, mode="light"):
    """Helper function to analyze a screenshot with Ollama."""
    lock_fd = acquire_ollama_lock()
    try:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        prompt = f"""Please analyze this webpage screenshot ({mode} mode) and focus specifically on finding white backgrounds and contrast issues.

IMPORTANT: In dark mode, ANY white or light-colored backgrounds are problematic and must be reported.
Examples of what to look for:
- White or light-colored buttons
- Light backgrounds behind text
- White/light colored sections or panels
- Light colored headers or footers
- Any UI elements that appear too bright for dark mode

If you find ANY white or light backgrounds in dark mode, start your response with 'WARNING: White background detected:' and list each instance.

Please analyze:
1. Background colors and contrast - list any inconsistencies or contrast issues
2. Color scheme consistency - especially check for any white/light backgrounds that don't match the theme
3. Text readability against backgrounds
4. Interactive element visibility


Be extremely specific about colors, using terms like 'white', 'light gray', 'off-white' etc."""
        
        payload = {
            "model": "llama3.2-vision:11b",
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        }
        
        response = requests.post('http://localhost:11434/api/generate', json=payload)
        response.raise_for_status()
        return prompt, response.json()['response']
    finally:
        release_ollama_lock(lock_fd)
        # Add a small delay after releasing the lock to prevent immediate reacquisition
        time.sleep(0.5)

@pytest.mark.sequential
def test_visual_analysis_with_ollama(page):
    """Test the visual appearance of the homepage in both light and dark modes."""
    
    # First analyze in light mode
    page.goto('http://localhost:8888')
    page.wait_for_selector('text=Brevify')
    page.wait_for_selector('#url-input')
    
    # Wait for page to be fully loaded and stable
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(1000)  # Wait an extra second for stability
    
    light_screenshot = '/tmp/brevify_light_mode.png'
    page.screenshot(path=light_screenshot, full_page=True)
    print(f"\nSaved light mode screenshot to: {light_screenshot}")
    prompt, light_analysis = analyze_with_ollama(light_screenshot, "light")
    print("\n=== Light Mode Analysis ===")
    print("Prompt:")
    print(prompt)
    print("\nResponse:")
    print(light_analysis)
    print("==========================\n")
    
    # Wait for settings button to be visible and clickable
    page.wait_for_selector('#settings-button', state='visible')
    page.wait_for_timeout(500)  # Small delay before clicking
    
    try:
        # Click settings and enable dark mode
        page.click('#settings-button')
        page.wait_for_selector('#theme-select', state='visible')
        page.select_option('#theme-select', 'dark')
        
        # Wait for theme transition
        page.wait_for_timeout(1000)
        
        # Take dark mode screenshot
        dark_screenshot = '/tmp/brevify_dark_mode.png'
        page.screenshot(path=dark_screenshot, full_page=True)
        print(f"\nSaved dark mode screenshot to: {dark_screenshot}")
        prompt, dark_analysis = analyze_with_ollama(dark_screenshot, "dark")
        print("\n=== Dark Mode Analysis ===")
        print("Prompt:")
        print(prompt)
        print("\nResponse:")
        print(dark_analysis)
        print("==========================\n")
        
        print("\nAI REVIEW INSTRUCTIONS:")
        print("=======================")
        print("Please review the above light and dark mode analyses for the following:")
        print("1. DARK MODE: Check for any white or light-colored backgrounds that should be dark")
        print("2. CONTRAST: Verify text is readable against all backgrounds")
        print("3. THEME CONSISTENCY: Ensure UI elements follow the selected theme")
        print("5. UI/UX: Note any inconsistencies in the interface")
        print("=======================\n")
            
    except Exception as e:
        print(f"\nError during dark mode testing: {str(e)}")
        # Take a screenshot of the error state
        page.screenshot(path="/tmp/error_state.png")
        print(f"Error state screenshot saved to: /tmp/error_state.png")
        raise

if __name__ == '__main__':
    pytest.main(['-v', __file__])
