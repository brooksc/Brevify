"""
Test local storage functionality.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_settings_persistence(selenium):
    """Test settings are saved to local storage."""
    selenium.get('http://localhost:5000')
    
    # Set theme preference
    theme_toggle = selenium.find_element(By.ID, 'theme-toggle')
    theme_toggle.click()
    
    # Refresh page
    selenium.refresh()
    
    # Verify theme persisted
    body = selenium.find_element(By.TAG_NAME, 'body')
    assert 'dark-theme' in body.get_attribute('class')
    
    # Set AI service preference
    service_select = selenium.find_element(By.ID, 'default-ai-service')
    service_select.click()
    service_select.find_element(By.CSS_SELECTOR, '[value="claude"]').click()
    
    # Refresh page
    selenium.refresh()
    
    # Verify AI service preference persisted
    service_select = selenium.find_element(By.ID, 'default-ai-service')
    assert service_select.get_attribute('value') == 'claude'

def test_video_history(selenium):
    """Test video history management."""
    selenium.get('http://localhost:5000')
    
    # Process a video
    url_input = selenium.find_element(By.ID, 'video-url')
    url_input.send_keys('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    submit_button = selenium.find_element(By.ID, 'submit-url')
    submit_button.click()
    
    # Wait for processing to complete
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
    )
    
    # Verify video appears in history
    history_button = selenium.find_element(By.ID, 'history-button')
    history_button.click()
    
    history_items = selenium.find_elements(By.CLASS_NAME, 'history-item')
    assert len(history_items) == 1
    assert 'dQw4w9WgXcQ' in history_items[0].get_attribute('data-video-id')
    
    # Process another video
    url_input.clear()
    url_input.send_keys('https://www.youtube.com/watch?v=different_video')
    submit_button.click()
    
    # Wait for processing to complete
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
    )
    
    # Verify both videos in history
    history_items = selenium.find_elements(By.CLASS_NAME, 'history-item')
    assert len(history_items) == 2
    
    # Test history limit
    for i in range(20):  # History should be limited to 20 items
        url_input.clear()
        url_input.send_keys(f'https://www.youtube.com/watch?v=video_{i}')
        submit_button.click()
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
        )
    
    history_items = selenium.find_elements(By.CLASS_NAME, 'history-item')
    assert len(history_items) == 20
    assert 'dQw4w9WgXcQ' not in [item.get_attribute('data-video-id') for item in history_items]

def test_custom_prompts(selenium):
    """Test custom prompt template storage."""
    selenium.get('http://localhost:5000')
    
    # Create custom prompt
    settings_button = selenium.find_element(By.ID, 'settings-button')
    settings_button.click()
    
    add_prompt_button = selenium.find_element(By.ID, 'add-prompt-template')
    add_prompt_button.click()
    
    prompt_name = selenium.find_element(By.ID, 'prompt-name')
    prompt_name.send_keys('Test Template')
    
    prompt_content = selenium.find_element(By.ID, 'prompt-content')
    prompt_content.send_keys('Please analyze this: {transcript}')
    
    save_button = selenium.find_element(By.ID, 'save-prompt')
    save_button.click()
    
    # Refresh page
    selenium.refresh()
    
    # Verify prompt persisted
    settings_button = selenium.find_element(By.ID, 'settings-button')
    settings_button.click()
    
    prompt_templates = selenium.find_elements(By.CLASS_NAME, 'prompt-template')
    assert len(prompt_templates) == 1
    assert 'Test Template' in prompt_templates[0].text
