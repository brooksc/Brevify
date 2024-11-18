#!/usr/bin/env python3
"""
YouTube video transcription and channel information service.
Provides API endpoints for fetching video transcripts and channel information.
"""
from typing import Dict, List, Optional, Union
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)  # Enable CORS for all routes

# Configure Flask-Caching with a simple cache
cache_config = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes
    'CACHE_THRESHOLD': 100  # Maximum number of items in cache
}
cache = Cache(app, config=cache_config)

def get_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    try:
        patterns = {
            'video': r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            'short': r'youtu\.be\/([0-9A-Za-z_-]{11})'
        }
        for pattern in patterns.values():
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError('Invalid YouTube URL')
    except Exception as e:
        raise ValueError(f'Error getting video ID: {str(e)}') from e

def get_channel_id(url: str) -> str:
    """Extract channel ID from various YouTube URL formats."""
    try:
        patterns = {
            'channel': r'youtube\.com/channel/([^/?]+)',
            'user': r'(?:www\.)?youtube\.com/@([^/?]+)'
        }
        for pattern_type, pattern in patterns.items():
            match = re.search(pattern, url)
            if match:
                identifier = match.group(1)
                if pattern_type == 'channel' and identifier.startswith('UC'):
                    return identifier
                youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
                response = youtube.search().list(
                    part='snippet',
                    type='channel',
                    q=identifier
                ).execute()
                if response['items']:
                    return response['items'][0]['id']['channelId']
        raise ValueError('Invalid YouTube channel URL')
    except Exception as e:
        raise ValueError(f'Error getting channel ID: {str(e)}') from e

@cache.memoize(timeout=300)
def fetch_transcript(video_id: str) -> Dict[str, Union[bool, str, List[Dict[str, Union[str, float]]]]]:
    """Fetch transcript for a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return {
            'success': True,
            'transcript': transcript
        }
    except TranscriptsDisabled:
        raise ValueError('No transcript available')
    except Exception as e:
        raise ValueError(f'Error fetching transcript: {str(e)}')

@cache.memoize(timeout=300)
def fetch_channel_videos(channel_id: str) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    """Fetch recent videos from a YouTube channel."""
    try:
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # First try to get channel by username (for @handles)
        if channel_id.startswith('@'):
            username = channel_id.lstrip('@')
            channel_response = youtube.channels().list(
                part='snippet',
                forUsername=username
            ).execute()
            if not channel_response.get('items'):
                # Try search instead for @handles
                search_response = youtube.search().list(
                    part='snippet',
                    q=channel_id,
                    type='channel',
                    maxResults=1
                ).execute()
                
                if not search_response.get('items'):
                    raise ValueError('Channel not found')
                
                channel_id = search_response['items'][0]['id']['channelId']
                channel_response = youtube.channels().list(
                    part='snippet',
                    id=channel_id
                ).execute()
                
                if not channel_response.get('items'):
                    raise ValueError('Channel not found')
        else:
            # Try direct channel ID lookup
            channel_response = youtube.channels().list(
                part='snippet',
                id=channel_id
            ).execute()
            if not channel_response.get('items'):
                raise ValueError('Channel not found')
            
        channel_title = channel_response['items'][0]['snippet']['title']
        channel_id = channel_response['items'][0]['id']  # Get actual channel ID
        
        videos_response = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            order='date',
            type='video',
            maxResults=10
        ).execute()
        
        videos = []
        if videos_response and videos_response.get('items'):
            videos = [{
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'publishedAt': item['snippet']['publishedAt']
            } for item in videos_response['items']]
        
        return {
            'success': True,
            'channel_title': channel_title,
            'videos': videos
        }
    except Exception as e:
        if isinstance(e, HttpError):
            if e.resp.status == 404:
                raise ValueError('Channel not found')
            raise ValueError('Error fetching channel')
        if isinstance(e, ValueError):
            raise e
        raise ValueError('Error fetching channel')

@app.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/transcript')
def get_transcript():
    """API endpoint to fetch transcript for a YouTube video."""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400
        
        video_id = get_video_id(url)
        transcript_result = fetch_transcript(video_id)
        
        # Get video details
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        try:
            video_response = youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                return jsonify({'success': False, 'error': 'Video not found'}), 404
            return jsonify({'success': False, 'error': 'Error fetching video'}), 500
            
        if not video_response.get('items'):
            return jsonify({'success': False, 'error': 'Video not found'}), 404
            
        video_title = video_response['items'][0]['snippet']['title']
        
        return jsonify({
            'success': True,
            'video_title': video_title,
            'transcript': transcript_result['transcript']
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/videos')
def get_videos():
    """API endpoint to fetch videos from a YouTube channel."""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400
        
        channel_id = get_channel_id(url)
        result = fetch_channel_videos(channel_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/channel', methods=['POST'])
def add_channel():
    """Add a new YouTube channel."""
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        channel_id = get_channel_id(url)
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # Get channel details
        try:
            channel_response = youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                return jsonify({'error': 'Channel not found'}), 404
            return jsonify({'error': 'Error fetching channel'}), 500

        if not channel_response['items']:
            return jsonify({'error': 'Channel not found'}), 404

        channel_data = channel_response['items'][0]
        channel = {
            'id': channel_id,
            'name': channel_data['snippet']['title'],
            'url': url,
            'thumbnail': channel_data['snippet']['thumbnails']['default']['url'],
            'subscriberCount': int(channel_data['statistics']['subscriberCount']),
            'videoCount': int(channel_data['statistics']['videoCount']),
            'lastRefreshed': datetime.now().isoformat(),
            'isActive': True
        }

        return jsonify(channel)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/channel/<channel_id>', methods=['GET'])
def get_channel(channel_id):
    try:
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # Get channel details
        try:
            channel_response = youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                return jsonify({'error': 'Channel not found'}), 404
            return jsonify({'error': 'Error fetching channel'}), 500
            
        if not channel_response['items']:
            return jsonify({'error': 'Channel not found'}), 404
            
        channel = channel_response['items'][0]
        
        return jsonify({
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'thumbnail': channel['snippet']['thumbnails']['default']['url'],
            'subscriberCount': int(channel['statistics']['subscriberCount'])
        })
        
    except HttpError as e:
        return jsonify({'error': f'YouTube API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/channel/<channel_id>/videos', methods=['GET'])
def get_channel_videos(channel_id):
    try:
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # Get channel's uploaded videos playlist ID
        try:
            channel_response = youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                return jsonify({'error': 'Channel not found'}), 404
            return jsonify({'error': 'Error fetching channel'}), 500
            
        if not channel_response['items']:
            return jsonify({'error': 'Channel not found'}), 404
            
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get videos from uploads playlist
        videos = []
        next_page_token = None
        
        while True:
            try:
                playlist_items = youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
            except HttpError as e:
                if e.resp.status == 404:
                    return jsonify({'error': 'Playlist not found'}), 404
                return jsonify({'error': 'Error fetching playlist'}), 500
            
            video_ids = [item['contentDetails']['videoId'] for item in playlist_items['items']]
            
            # Get video details
            try:
                video_response = youtube.videos().list(
                    part='snippet,contentDetails,statistics',
                    id=','.join(video_ids)
                ).execute()
            except HttpError as e:
                if e.resp.status == 404:
                    return jsonify({'error': 'Video not found'}), 404
                return jsonify({'error': 'Error fetching video'}), 500
            
            for video in video_response['items']:
                videos.append({
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'thumbnail': video['snippet']['thumbnails']['medium']['url'],
                    'publishedAt': video['snippet']['publishedAt'],
                    'duration': video['contentDetails']['duration'],
                    'viewCount': int(video['statistics']['viewCount']),
                    'channelId': channel_id
                })
            
            next_page_token = playlist_items.get('nextPageToken')
            if not next_page_token:
                break
        
        return jsonify(videos)
        
    except HttpError as e:
        return jsonify({'error': f'YouTube API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/service/<service_id>/<video_id>', methods=['GET'])
def get_service_result(service_id, video_id):
    """Get the result of an AI service for a specific video."""
    try:
        # Check if we have a cached result
        cache_key = f'service_{service_id}_{video_id}'
        cached_result = cache.get(cache_key)
        if cached_result:
            return jsonify(cached_result)

        # Get video transcript first
        transcript_data = fetch_transcript(video_id)
        if not transcript_data['success']:
            return jsonify({'error': 'Failed to fetch transcript'}), 400

        # Process transcript based on service type
        if service_id == 'transcript':
            result = {
                'success': True,
                'result': transcript_data['transcript']
            }
        elif service_id == 'summary':
            # Combine transcript text
            full_text = ' '.join([entry['text'] for entry in transcript_data['transcript']])
            
            # TODO: Implement OpenAI GPT-3 summary generation
            # For now, return a placeholder
            result = {
                'success': True,
                'result': 'Summary generation coming soon!'
            }
        elif service_id == 'topics':
            # Combine transcript text
            full_text = ' '.join([entry['text'] for entry in transcript_data['transcript']])
            
            # TODO: Implement topic extraction
            # For now, return placeholder topics
            result = {
                'success': True,
                'result': ['Topic extraction coming soon!']
            }
        else:
            return jsonify({'error': f'Unknown service: {service_id}'}), 400

        # Cache the result
        cache.set(cache_key, result)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)