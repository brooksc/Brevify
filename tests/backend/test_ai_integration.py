"""
Test AI integration functionality.
"""
import pytest
from transcribe import generate_prompt, generate_ai_url

def test_generate_prompt():
    """Test prompt template generation."""
    transcript = "This is a test transcript"
    
    # Test default prompt
    prompt = generate_prompt(transcript)
    assert "This is a test transcript" in prompt
    assert "Please analyze this YouTube video transcript carefully" in prompt
    assert "Key points" in prompt
    assert "main ideas" in prompt
    
    # Test long transcript handling
    long_transcript = "word " * 5000  # Approximately 25k characters
    prompt = generate_prompt(long_transcript)
    assert len(prompt) <= 30000  # Ensure it fits AI service limits
    assert "[transcript truncated]" in prompt
    
    # Test custom prompt template
    custom_template = "Please summarize this: {transcript}"
    prompt = generate_prompt(transcript, template=custom_template)
    assert prompt == "Please summarize this: This is a test transcript"

def test_generate_ai_url():
    """Test AI service URL generation."""
    transcript = "Test transcript"
    prompt = generate_prompt(transcript)
    
    # Test ChatGPT URL
    chatgpt_url = generate_ai_url(prompt, 'chatgpt')
    assert 'chat.openai.com/chat' in chatgpt_url
    assert 'text=' in chatgpt_url
    
    # Test Claude URL
    claude_url = generate_ai_url(prompt, 'claude')
    assert 'claude.ai' in claude_url
    assert 'text=' in claude_url
    
    # Test Gemini URL
    gemini_url = generate_ai_url(prompt, 'gemini')
    assert 'gemini.google.com' in gemini_url
    assert 'text=' in gemini_url
    
    # Test invalid service
    with pytest.raises(ValueError) as exc_info:
        generate_ai_url(prompt, 'invalid_service')
    assert "Unsupported AI service" in str(exc_info.value)

def test_prompt_variables():
    """Test prompt template variable substitution."""
    transcript = "Test transcript"
    metadata = {
        'title': 'Test Video',
        'channel': 'Test Channel',
        'duration': '10:00'
    }
    
    template = """
    Title: {title}
    Channel: {channel}
    Duration: {duration}
    
    Transcript:
    {transcript}
    
    Please analyze this content.
    """
    
    prompt = generate_prompt(transcript, template=template, metadata=metadata)
    assert 'Title: Test Video' in prompt
    assert 'Channel: Test Channel' in prompt
    assert 'Duration: 10:00' in prompt
    assert 'Test transcript' in prompt
