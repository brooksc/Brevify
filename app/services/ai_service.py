"""AI service integration for Brevify.

This module handles interactions with various AI services for processing YouTube transcripts.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AIServiceType(Enum):
    """Supported AI service types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

@dataclass
class PromptTemplate:
    """Template for generating AI prompts."""
    name: str
    template: str
    description: str
    default_params: Dict[str, str]

@dataclass
class AIServiceConfig:
    """Configuration for an AI service."""
    service_type: AIServiceType
    api_key_env: str
    model: str
    max_tokens: int
    temperature: float

class AIService:
    """Main class for AI service integration."""
    
    DEFAULT_TEMPLATES = {
        "summarize": PromptTemplate(
            name="summarize",
            template="Summarize the following transcript in a clear and concise way:\n\n{transcript}",
            description="Generate a concise summary of the video",
            default_params={"max_length": "500"}
        ),
        "key_points": PromptTemplate(
            name="key_points",
            template="Extract the main key points from this transcript:\n\n{transcript}",
            description="Extract key points and insights",
            default_params={"format": "bullet_points"}
        ),
        "study_guide": PromptTemplate(
            name="study_guide",
            template="Create a study guide from this transcript with sections for key concepts, definitions, and practice questions:\n\n{transcript}",
            description="Generate a comprehensive study guide",
            default_params={"include_questions": "true"}
        )
    }

    def __init__(self, config: AIServiceConfig):
        """Initialize the AI service with configuration."""
        self.config = config
        self.templates = self.DEFAULT_TEMPLATES.copy()

    def add_template(self, template: PromptTemplate) -> None:
        """Add a new prompt template."""
        self.templates[template.name] = template

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name."""
        return self.templates.get(name)

    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())

    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with provided parameters."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Merge default params with provided kwargs
        params = template.default_params.copy()
        params.update(kwargs)
        
        return template.template.format(**params)

    async def process_transcript(self, template_name: str, transcript: str, **kwargs) -> str:
        """Process a transcript using the specified template and AI service."""
        prompt = self.format_prompt(template_name, transcript=transcript, **kwargs)
        
        # TODO: Implement actual AI service calls based on self.config.service_type
        # This will be implemented in the next iteration
        return f"Processed with {self.config.service_type.value}: {prompt[:100]}..."

    def get_launch_url(self, template_name: str, transcript: str) -> str:
        """Get a URL to launch the AI service in a new tab with context."""
        # TODO: Implement service-specific URL generation
        return f"https://example.com/ai?template={template_name}&text={transcript[:100]}"
