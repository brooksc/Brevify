"""Component for rendering video lists."""

from typing import List
from app.services.youtube_service import Video

class VideoList:
    """Component for rendering a list of videos."""
    
    def __init__(self, videos: List[Video]):
        """Initialize with a list of videos."""
        self.videos = videos
        
        # Clean up video descriptions
        for video in self.videos:
            video.description = self._clean_description(video.description)
    
    def process_videos(self) -> List[Video]:
        """Process videos to add transcripts and AI URLs."""
        from app.services.ai_url_service import AIURLService
        ai_service = AIURLService()
        
        for video in self.videos:
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                from youtube_transcript_api.formatters import TextFormatter
                
                transcript_list = YouTubeTranscriptApi.get_transcript(video.id)
                formatter = TextFormatter()
                video.transcript = formatter.format_transcript(transcript_list)
                
                # Generate AI URLs
                if video.transcript:
                    video.chatgpt_url = ai_service.get_chatgpt_url(video.transcript)
                    video.claude_url = ai_service.get_claude_url(video.transcript)
                    video.gemini_url = ai_service.get_gemini_url(video.transcript)
            except Exception as e:
                # If transcript fails, just continue without it
                pass
                
        return self.videos
    
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
    
    def render(self) -> str:
        """Render the video list as HTML."""
        if not self.videos:
            return '<div class="text-center text-gray-500">No videos found</div>'
        
        html = ['<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">']
        
        for video in self.videos:
            html.append(self._render_video_card(video))
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _render_video_card(self, video: Video) -> str:
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
                        {video.description}
                    </p>
                    {ai_tools_html}
                </div>
            </div>
        """
