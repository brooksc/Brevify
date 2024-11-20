#!/usr/bin/env python3
"""
YouTube video transcription and channel information service.
Provides API endpoints for fetching video transcripts and channel information.
"""
from typing import Dict, List, Optional, Union
from flask import Flask, jsonify, request, render_template, send_from_directory, url_for
from flask_cors import CORS
from flask_caching import Cache
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import quote

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
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
    """Extract channel ID from URL and resolve handles using YouTube API if needed."""
    if not url:
        raise ValueError('Invalid YouTube channel URL')

    # Direct channel ID pattern
    channel_match = re.search(r'youtube\.com/channel/([^/?&]+)', url)
    if channel_match:
        return channel_match.group(1)
    
    # Handle/Custom URL patterns
    handle_match = re.search(r'youtube\.com/(?:c/|@|user/)?([^/?&]+)', url)
    if not handle_match:
        raise ValueError('Invalid YouTube channel URL')
    
    handle = handle_match.group(1)
    
    try:
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # Try to find channel by handle/custom URL
        search_response = youtube.search().list(
            part='snippet',
            q=handle,
            type='channel',
            maxResults=1
        ).execute()
        
        if not search_response.get('items'):
            raise ValueError('Channel not found')
            
        return search_response['items'][0]['id']['channelId']
    except HttpError as e:
        if e.resp.status == 403:
            raise ValueError('YouTube API quota exceeded')
        raise ValueError(f'Error accessing YouTube API: {str(e)}')
    except Exception as e:
        raise ValueError(f'Error resolving channel ID: {str(e)}')

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

def generate_prompt(transcript: str, template: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
    """Generate a prompt for AI analysis."""
    if not template:
        template = """
Please analyze this YouTube video transcript carefully and provide:
1. Key points and main ideas
2. Important insights and takeaways
3. Any notable quotes or statements
4. A brief summary

Transcript:
{transcript}
"""
    
    # Create format dictionary with transcript
    format_dict = {'transcript': transcript}
    
    # Add metadata to format dictionary if provided
    if metadata:
        format_dict.update(metadata)
    
    # Format template with variables
    try:
        result = template.format(**format_dict)
    except KeyError as e:
        raise ValueError(f'Missing required variable in template: {str(e)}')
    
    # Handle long prompts
    if len(result) > 30000:
        # Calculate available space for transcript
        template_without_transcript = template.format(**{**format_dict, 'transcript': ''})
        available_space = 30000 - len(template_without_transcript)
        
        # Truncate transcript and add indicator
        truncated_transcript = transcript[:available_space] + "\n[transcript truncated]"
        format_dict['transcript'] = truncated_transcript
        result = template.format(**format_dict)
    
    return result

def fetch_channel_videos(channel_id: str, max_results: int = 10) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    """Fetch videos from a YouTube channel."""
    try:
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # First verify channel exists
        try:
            channel_response = youtube.channels().list(
                part='snippet',
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                raise ValueError('Channel not found')
            
            channel_info = channel_response['items'][0]['snippet']
            
            # Then get channel videos
            videos_response = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=max_results,
                type='video',
                order='date'
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail_url': item['snippet']['thumbnails']['medium']['url'],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video)
            
            return {
                'success': True,
                'channel_title': channel_info['title'],
                'videos': videos
            }
            
        except HttpError as e:
            if e.resp.status == 403:
                raise ValueError('YouTube API quota exceeded')
            if e.resp.status == 404:
                raise ValueError('Channel not found')
            raise ValueError(f'Error accessing YouTube API: {str(e)}')
            
    except Exception as e:
        raise ValueError(f'Error fetching channel: {str(e)}')

def generate_ai_url(prompt, service):
    """Generate URL for AI service with pre-filled prompt."""
    encoded_prompt = quote(prompt)
    
    if service == 'chatgpt':
        return f'https://chat.openai.com/chat?text={encoded_prompt}'
    elif service == 'claude':
        return f'https://claude.ai?text={encoded_prompt}'
    elif service == 'gemini':
        return f'https://gemini.google.com?text={encoded_prompt}'
    else:
        raise ValueError(f"Unsupported AI service: {service}")

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/api/videos')
def get_videos():
    """API endpoint to fetch videos from a YouTube channel."""
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        channel_id = get_channel_id(url)
        videos = fetch_channel_videos(channel_id)
        return jsonify(videos)
    except ValueError as e:
        error_msg = str(e)
        if 'Invalid YouTube channel URL' in error_msg:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        if 'Channel not found' in error_msg:
            return jsonify({'error': 'Channel not found'}), 404
        return jsonify({'error': error_msg}), 500

@app.route('/api/transcript')
def get_transcript():
    """API endpoint to fetch transcript for a YouTube video."""
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        video_id = get_video_id(url)
        result = fetch_transcript(video_id)
        return jsonify(result)
    except ValueError as e:
        error_msg = str(e)
        if 'Invalid YouTube URL' in error_msg:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        if 'No transcript available' in error_msg:
            return jsonify({'error': 'No transcript available'}), 404
        return jsonify({'error': error_msg}), 500

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
    # Only enable debug mode when running directly
    debug_mode = os.environ.get('FLASK_ENV') != 'testing'
    port = int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=True)