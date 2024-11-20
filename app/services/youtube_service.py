"""Service for interacting with YouTube API and fetching video data."""

import os
import logging
from typing import List, Optional
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

logger = logging.getLogger(__name__)

@dataclass
class Video:
    """Data class to hold video information."""
    id: str
    title: str
    description: str
    thumbnail_url: str
    transcript: Optional[str] = None
    chatgpt_url: Optional[str] = None
    claude_url: Optional[str] = None
    gemini_url: Optional[str] = None

class YouTubeService:
    """Service for interacting with YouTube API."""
    
    def __init__(self):
        """Initialize the YouTube service with API key."""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.formatter = TextFormatter()
    
    def _extract_channel_id(self, channel_url: str) -> str:
        """Extract channel ID from various YouTube channel URL formats."""
        logger.debug(f"Extracting channel ID from URL: {channel_url}")
        
        # Handle @username format
        if '@' in channel_url:
            username = channel_url.split('@')[-1].split('/')[0]
            logger.debug(f"Found username: {username}")
            
            # Search for the channel
            try:
                request = self.youtube.search().list(
                    part='snippet',
                    q=username,
                    type='channel',
                    maxResults=1
                )
                response = request.execute()
                
                if response['items']:
                    channel_id = response['items'][0]['id']['channelId']
                    logger.debug(f"Found channel ID for username: {channel_id}")
                    return channel_id
                else:
                    raise ValueError(f"Could not find channel for username: {username}")
            except Exception as e:
                logger.error(f"Error searching for channel: {str(e)}")
                raise ValueError(f"Could not find channel: {str(e)}")
        
        # Handle standard URL formats
        parsed_url = urlparse(channel_url)
        path_parts = parsed_url.path.split('/')
        
        if '/channel/' in channel_url:
            channel_id = path_parts[path_parts.index('channel') + 1]
            logger.debug(f"Found channel ID in URL: {channel_id}")
            return channel_id
        elif '/c/' in channel_url or '/user/' in channel_url:
            # Handle custom URLs
            custom_id = path_parts[-1]
            logger.debug(f"Found custom URL: {custom_id}")
            
            try:
                request = self.youtube.search().list(
                    part='snippet',
                    q=custom_id,
                    type='channel',
                    maxResults=1
                )
                response = request.execute()
                
                if response['items']:
                    channel_id = response['items'][0]['id']['channelId']
                    logger.debug(f"Found channel ID for custom URL: {channel_id}")
                    return channel_id
                else:
                    raise ValueError(f"Could not find channel for custom URL: {custom_id}")
            except Exception as e:
                logger.error(f"Error searching for channel: {str(e)}")
                raise ValueError(f"Could not find channel: {str(e)}")
        
        logger.error("Invalid YouTube channel URL format")
        raise ValueError("Invalid YouTube channel URL format")

    def get_channel_videos(self, channel_url: str, max_results: int = 10) -> List[Video]:
        """Get videos from a YouTube channel with transcripts."""
        try:
            channel_id = self._extract_channel_id(channel_url)
            logger.debug(f"Using channel ID: {channel_id}")
            
            # Get channel's uploads playlist
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                raise ValueError("Channel not found")
            
            playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            logger.debug(f"Found uploads playlist: {playlist_id}")
            
            # Get videos from uploads playlist
            videos_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in videos_response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                logger.debug(f"Processing video: {video_id}")
                
                video = Video(
                    id=video_id,
                    title=item['snippet']['title'],
                    description=item['snippet']['description'],
                    thumbnail_url=item['snippet']['thumbnails']['high']['url']
                )
                
                # Try to get transcript
                try:
                    logger.debug(f"Fetching transcript for video {video_id}")
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    video.transcript = self.formatter.format_transcript(transcript)
                    logger.debug("Transcript fetched successfully")
                except Exception as e:
                    logger.warning(f"Could not get transcript for video {video_id}: {str(e)}")
                    video.transcript = None
                
                videos.append(video)
            
            logger.debug(f"Successfully fetched {len(videos)} videos")
            return videos
            
        except Exception as e:
            logger.error(f"Error fetching channel videos: {str(e)}")
            raise ValueError(f"Error fetching channel videos: {str(e)}")