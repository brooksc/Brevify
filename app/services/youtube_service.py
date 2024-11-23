"""Service for interacting with YouTube API."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from sqlalchemy.orm import Session
from app.models.db_models import Channel, Video as DBVideo
from app.db.database import get_db

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service for fetching YouTube data."""

    def __init__(self):
        """Initialize the service."""
        self.db = next(get_db())

    async def get_channel_info(self, channel_url: str) -> Optional[Channel]:
        """Get channel info, first checking cache then YouTube."""
        # Extract channel ID from URL
        channel_id = self._extract_channel_id(channel_url)
        
        # Check cache first
        cached_channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
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
            else:
                # Create new channel
                cached_channel = Channel(**channel_info)
                self.db.add(cached_channel)
            
            self.db.commit()
            return cached_channel
        except Exception as e:
            logger.error(f"Error fetching channel info: {e}")
            return cached_channel if cached_channel else None

    async def get_videos(self, channel_id: str) -> List[DBVideo]:
        """Get videos for a channel, using cache when possible."""
        # Check cache first
        cached_videos = self.db.query(DBVideo).filter(
            DBVideo.channel_id == channel_id
        ).order_by(DBVideo.published_at.desc()).all()

        # Get latest video date
        latest_date = None
        if cached_videos:
            latest_date = max(v.published_at for v in cached_videos)

        # Fetch new videos from YouTube
        try:
            new_videos = self._fetch_videos_from_youtube(channel_id, after_date=latest_date)
            for video_info in new_videos:
                video = DBVideo(**video_info)
                self.db.add(video)
            
            self.db.commit()
            
            # Return all videos, including new ones
            return self.db.query(DBVideo).filter(
                DBVideo.channel_id == channel_id
            ).order_by(DBVideo.published_at.desc()).all()
        except Exception as e:
            logger.error(f"Error fetching videos: {e}")
            return cached_videos if cached_videos else []

    async def get_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript for a video, using cache when possible."""
        # Check cache first
        video = self.db.query(DBVideo).filter(DBVideo.id == video_id).first()
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
                self.db.commit()

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
        # Handle @username format
        if '@' in url:
            username = url.split('@')[-1].split('/')[0]
            logger.debug(f"Found username: {username}")
            
            # Search for the channel
            try:
                api_key = os.getenv('YOUTUBE_API_KEY')
                youtube = build('youtube', 'v3', developerKey=api_key)
                request = youtube.search().list(
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
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        if '/channel/' in url:
            channel_id = path_parts[path_parts.index('channel') + 1]
            logger.debug(f"Found channel ID in URL: {channel_id}")
            return channel_id
        elif '/c/' in url or '/user/' in url:
            # Handle custom URLs
            custom_id = path_parts[-1]
            logger.debug(f"Found custom URL: {custom_id}")
            
            try:
                api_key = os.getenv('YOUTUBE_API_KEY')
                youtube = build('youtube', 'v3', developerKey=api_key)
                request = youtube.search().list(
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

    def _fetch_channel_from_youtube(self, channel_id: str) -> dict:
        """Fetch channel info from YouTube."""
        try:
            api_key = os.getenv('YOUTUBE_API_KEY')
            youtube = build('youtube', 'v3', developerKey=api_key)
            channel_response = youtube.channels().list(
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
                'thumbnail_url': channel_info['snippet']['thumbnails']['high']['url']
            }
        except Exception as e:
            logger.error(f"Error fetching channel info: {e}")
            raise ValueError(f"Error fetching channel info: {e}")

    def _fetch_videos_from_youtube(self, channel_id: str, after_date: Optional[datetime] = None) -> List[dict]:
        """Fetch videos from YouTube."""
        try:
            api_key = os.getenv('YOUTUBE_API_KEY')
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Get channel's uploads playlist
            channel_response = youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                raise ValueError("Channel not found")
            
            playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            logger.debug(f"Found uploads playlist: {playlist_id}")
            
            # Get videos from uploads playlist
            videos_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=10
            ).execute()
            
            videos = []
            for item in videos_response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                logger.debug(f"Processing video: {video_id}")
                
                video = {
                    'id': video_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': channel_id
                }
                
                # Try to get transcript
                try:
                    logger.debug(f"Fetching transcript for video {video_id}")
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    formatter = TextFormatter()
                    transcript = formatter.format_transcript(transcript_list)
                    video['transcript'] = transcript
                    logger.debug("Transcript fetched successfully")
                except Exception as e:
                    logger.warning(f"Could not get transcript for video {video_id}: {str(e)}")
                    video['transcript'] = None
                
                videos.append(video)
            
            logger.debug(f"Successfully fetched {len(videos)} videos")
            return videos
        except Exception as e:
            logger.error(f"Error fetching videos: {e}")
            raise ValueError(f"Error fetching videos: {e}")