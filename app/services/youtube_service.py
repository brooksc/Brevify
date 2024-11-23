"""Service for interacting with YouTube API."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from sqlmodel import Session, select
from app.models.models import Channel, Video
from googleapiclient.discovery import build
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service for fetching YouTube data."""

    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
        self.youtube = None
        api_key = os.getenv('YOUTUBE_API_KEY')
        if api_key:
            self.youtube = build('youtube', 'v3', developerKey=api_key)

    async def get_channel_info(self, channel_url: str) -> Optional[Channel]:
        """Get channel info, first checking cache then YouTube."""
        # Extract channel ID from URL
        channel_id = self._extract_channel_id(channel_url)
        
        # Check cache first
        statement = select(Channel).where(Channel.id == channel_id)
        cached_channel = self.db.exec(statement).first()
        if cached_channel and self._is_cache_fresh(cached_channel.last_fetched):
            return cached_channel

        # If not in cache or stale, fetch from YouTube
        try:
            channel_info = self._fetch_channel_from_youtube(channel_id)
            if cached_channel:
                # Update existing channel
                for key, value in channel_info.items():
                    setattr(cached_channel, key, value)
                cached_channel.last_fetched = datetime.utcnow()
                self.db.add(cached_channel)
            else:
                # Create new channel
                cached_channel = Channel(**channel_info)
                self.db.add(cached_channel)
            
            self.db.commit()
            return cached_channel
        except Exception as e:
            logger.error(f"Error fetching channel info: {e}")
            return None

    async def get_videos(self, channel_id: str) -> List[Video]:
        """Get videos for a channel, using cache when possible."""
        # Check cache first
        statement = select(Video).where(Video.channel_id == channel_id).order_by(Video.published_at.desc())
        cached_videos = self.db.exec(statement).all()

        # Get latest video date
        latest_date = None
        if cached_videos:
            latest_date = max(v.published_at for v in cached_videos)

        # Fetch new videos from YouTube
        try:
            new_videos_data = self._fetch_videos_from_youtube(channel_id, after_date=latest_date)
            new_videos = []
            for video_data in new_videos_data:
                video = Video(**video_data)
                self.db.add(video)
                new_videos.append(video)
            
            if new_videos:
                self.db.commit()
                for video in new_videos:
                    self.db.refresh(video)
                cached_videos.extend(new_videos)
            
            return sorted(cached_videos, key=lambda x: x.published_at, reverse=True)
        except Exception as e:
            logger.error(f"Error fetching videos: {e}")
            return cached_videos if cached_videos else []

    async def get_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript for a video, using cache when possible."""
        # Check cache first
        statement = select(Video).where(Video.id == video_id)
        video = self.db.exec(statement).first()
        if video and video.transcript:
            return video.transcript

        # If not in cache, fetch from YouTube
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = TextFormatter()
            transcript = formatter.format_transcript(transcript_list)

            # Cache the transcript
            if video:
                video.transcript = transcript
                video.transcript_fetched = datetime.utcnow()
                self.db.add(video)
                self.db.commit()
                self.db.refresh(video)

            return transcript
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            return None

    def _is_cache_fresh(self, last_fetched: datetime, max_age_hours: int = 24) -> bool:
        """Check if cached data is fresh enough."""
        if not last_fetched:
            return False
        return datetime.utcnow() - last_fetched < timedelta(hours=max_age_hours)

    def _extract_channel_id(self, url: str) -> str:
        """Extract channel ID from URL."""
        if not self.youtube:
            raise ValueError("YouTube API key not configured")

        # Handle @username format
        if '@' in url:
            username = url.split('@')[-1].split('/')[0]
            request = self.youtube.search().list(
                part='snippet',
                q=username,
                type='channel',
                maxResults=1
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]['id']['channelId']
            raise ValueError(f"Could not find channel for username: {username}")
            
        # Handle direct channel URLs
        if '/channel/' in url:
            return url.split('/channel/')[-1].split('/')[0]
            
        # Handle custom URLs
        if '/c/' in url or '/user/' in url:
            custom_id = url.split('/')[-1]
            request = self.youtube.search().list(
                part='snippet',
                q=custom_id,
                type='channel',
                maxResults=1
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]['id']['channelId']
            raise ValueError(f"Could not find channel for custom URL: {custom_id}")
            
        raise ValueError("Invalid YouTube channel URL format")

    def _fetch_channel_from_youtube(self, channel_id: str) -> dict:
        """Fetch channel info from YouTube."""
        if not self.youtube:
            raise ValueError("YouTube API key not configured")

        try:
            channel_response = self.youtube.channels().list(
                part='snippet,contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                raise ValueError("Channel not found")
            
            channel_info = channel_response['items'][0]
            return {
                'id': channel_info['id'],
                'title': channel_info['snippet']['title'],
                'description': channel_info['snippet']['description'],
                'thumbnail_url': channel_info['snippet']['thumbnails']['high']['url'],
                'url': f"https://youtube.com/channel/{channel_info['id']}"
            }
        except Exception as e:
            logger.error(f"Error fetching channel info: {e}")
            raise ValueError(f"Error fetching channel info: {e}")

    def _fetch_videos_from_youtube(self, channel_id: str, after_date: Optional[datetime] = None) -> List[dict]:
        """Fetch videos from YouTube."""
        if not self.youtube:
            raise ValueError("YouTube API key not configured")

        try:
            # Get channel's uploads playlist
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                raise ValueError("Channel not found")
            
            playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            videos_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50  # Increased to get more videos
            ).execute()
            
            videos = []
            for item in videos_response['items']:
                snippet = item['snippet']
                published_at = datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                
                # Skip if we already have newer videos
                if after_date and published_at <= after_date:
                    continue
                
                video_data = {
                    'id': snippet['resourceId']['videoId'],
                    'channel_id': channel_id,
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'thumbnail_url': snippet['thumbnails']['high']['url'],
                    'published_at': published_at,
                    'url': f"https://youtube.com/watch?v={snippet['resourceId']['videoId']}"
                }
                videos.append(video_data)
            
            return videos
        except Exception as e:
            logger.error(f"Error fetching videos: {e}")
            raise ValueError(f"Error fetching videos: {e}")