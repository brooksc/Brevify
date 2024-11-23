"""Component for rendering video lists."""

from typing import List, Optional
from app.models.models import Video
from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

class VideoList:
    """Component for rendering a list of videos."""
    
    def __init__(self, templates: Jinja2Templates):
        """Initialize with a Jinja2Templates instance."""
        self.templates = templates
        
    async def render(self, request: Request, videos: List[Video]):
        """Render the video list template"""
        return self.templates.TemplateResponse(
            "video_list.html",
            {"request": request, "videos": videos}
        )
    
    def _clean_description(self, description: str) -> str:
        """Clean up a video description."""
        if not description:
            return ""
            
        # Remove timestamps section and everything after
        if "Timestamps:" in description:
            description = description.split("Timestamps:")[0]
            
        # Remove common YouTube video sections
        sections_to_remove = [
            "----",
            "Key Takeaways:",
            "Join this channel",
            "Follow me on",
            "SUBSCRIBE",
            "Links:",
            "Resources:"
        ]
        
        for section in sections_to_remove:
            if section in description:
                description = description.split(section)[0]
                
        # Clean up line breaks and whitespace
        lines = [line.strip() for line in description.split('\n')]
        lines = [line for line in lines if line]
        description = ' '.join(lines)
        import re
        description = re.sub(r'\s+', ' ', description)
        return description.strip()
