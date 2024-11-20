"""Service for generating AI tool URLs from video transcripts."""

import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

class AIURLService:
    """Service for generating URLs to AI tools with video transcripts."""
    
    def __init__(self):
        """Initialize the AI URL service."""
        self.base_urls = {
            'chatgpt': "https://chat.openai.com/",
            'claude': "https://claude.ai/chat",
            'gemini': "https://gemini.google.com/"
        }
        
        self.prompt_templates = {
            'default': """I want to learn from this video transcript. Please analyze it and help me understand:
1. Key concepts and main ideas
2. Important terminology and definitions
3. Practical applications
4. Follow-up questions for deeper understanding

Transcript:
{transcript}"""
        }
    
    def _format_prompt(self, transcript: str) -> str:
        """Format the prompt with the transcript."""
        return self.prompt_templates['default'].format(transcript=transcript)
    
    def get_chatgpt_url(self, transcript: str) -> str:
        """Generate a ChatGPT URL with the video transcript."""
        try:
            prompt = self._format_prompt(transcript)
            params = f"?model=gpt-4&q={quote(prompt)}"
            return f"{self.base_urls['chatgpt']}{params}"
        except Exception as e:
            logger.error(f"Error generating ChatGPT URL: {str(e)}")
            return ""
    
    def get_claude_url(self, transcript: str) -> str:
        """Generate a Claude URL with the video transcript."""
        try:
            prompt = self._format_prompt(transcript)
            params = f"?prompt={quote(prompt)}"
            return f"{self.base_urls['claude']}{params}"
        except Exception as e:
            logger.error(f"Error generating Claude URL: {str(e)}")
            return ""
    
    def get_gemini_url(self, transcript: str) -> str:
        """Generate a Gemini URL with the video transcript."""
        try:
            prompt = self._format_prompt(transcript)
            params = f"?prompt={quote(prompt)}"
            return f"{self.base_urls['gemini']}{params}"
        except Exception as e:
            logger.error(f"Error generating Gemini URL: {str(e)}")
            return ""
