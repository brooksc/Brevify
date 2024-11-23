"""Component for rendering video lists."""

from typing import List, Optional
from app.models.video import Video
from app.services.youtube_service import YouTubeService, Video as YoutubeVideo
from fastapi import Request
from fastapi.templating import Jinja2Templates

class VideoList:
    """Component for rendering a list of videos."""
    
    def __init__(self, templates: Jinja2Templates):
        """Initialize with a Jinja2Templates instance."""
        self.templates = templates
        self.youtube_service = YouTubeService()
        
    async def render(self, request: Request, videos: List[Video]):
        """Render the video list template"""
        return self.templates.TemplateResponse(
            "video_list.html",
            {"request": request, "videos": videos}
        )
    
    async def get_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript for a specific video on-demand"""
        return await self.youtube_service.get_transcript(video_id)
    
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
        
        # Clean up remaining text
        lines = []
        for line in description.splitlines():
            line = line.strip()
            if line and not line.startswith(('🌟', '🚀', '💡', '🔧', '🎨', '🔥', '💻')):
                lines.append(line)
        
        # Join lines and clean up extra whitespace
        description = ' '.join(lines)
        import re
        description = re.sub(r'\s+', ' ', description)
        return description.strip()
    
    def process_videos(self, videos: List[YoutubeVideo]) -> List[YoutubeVideo]:
        """Process videos to add transcripts and AI URLs."""
        from app.services.ai_url_service import AIURLService
        ai_service = AIURLService()
        
        for video in videos:
            try:
                transcript = self.get_transcript(video.id)
                if transcript:
                    video.transcript = transcript
                    video.chatgpt_url = ai_service.get_chatgpt_url(video.transcript)
                    video.claude_url = ai_service.get_claude_url(video.transcript)
                    video.gemini_url = ai_service.get_gemini_url(video.transcript)
            except Exception as e:
                # If transcript fails, just continue without it
                pass
                
        return videos
    
    def _render_video_card(self, video: YoutubeVideo) -> str:
        """Render a single video card."""
        ai_tools = []
        if video.transcript:
            if video.chatgpt_url:
                ai_tools.append(
                    f'<a href="{video.chatgpt_url}" target="_blank" '
                    'class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200">'
                    'Analyze with ChatGPT</a>'
                )
            if video.claude_url:
                ai_tools.append(
                    f'<a href="{video.claude_url}" target="_blank" '
                    'class="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-200">'
                    'Analyze with Claude</a>'
                )
            if video.gemini_url:
                ai_tools.append(
                    f'<a href="{video.gemini_url}" target="_blank" '
                    'class="text-emerald-600 hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-200">'
                    'Analyze with Gemini</a>'
                )
        
        ai_tools_html = (
            '<div class="flex flex-col space-y-2 mt-2">' + 
            '\n'.join(ai_tools) + 
            '</div>'
        ) if ai_tools else (
            '<div class="text-gray-500 dark:text-gray-400 mt-2">'
            'No transcript available</div>'
        )
        
        return f"""
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                <a href="https://youtube.com/watch?v={video.id}" target="_blank" class="block">
                    <img src={video.thumbnail_url} alt="{video.title}" 
                         class="w-full h-48 object-cover">
                </a>
                <div class="p-4">
                    <a href="https://youtube.com/watch?v={video.id}" target="_blank"
                       class="text-lg font-semibold text-gray-900 dark:text-white hover:text-blue-600 
                              dark:hover:text-blue-400 line-clamp-2">
                        {video.title}
                    </a>
                    <p class="mt-2 text-gray-600 dark:text-gray-300 text-sm line-clamp-3">
                        {self._clean_description(video.description)}
                    </p>
                    {ai_tools_html}
                </div>
            </div>
        """
