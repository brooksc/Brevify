#!/usr/bin/env python3
"""
Script to fetch test data from YouTube and save it to a JSON file.
This helps maintain up-to-date test data for our test suite.
"""

import json
import os
from typing import Dict, List, Any
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

def load_test_inputs(file_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load test inputs from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def fetch_channel_data(youtube, channel: Dict[str, str]) -> Dict[str, Any]:
    """Fetch channel data including recent videos."""
    # First get channel info
    channel_response = youtube.channels().list(
        part='snippet',
        forUsername=channel['handle'].lstrip('@')
    ).execute()

    if not channel_response.get('items'):
        # Try searching by handle if direct lookup fails
        search_response = youtube.search().list(
            part='snippet',
            q=channel['handle'],
            type='channel',
            maxResults=1
        ).execute()
        
        if not search_response.get('items'):
            raise ValueError(f"Channel not found: {channel['handle']}")
        
        channel_id = search_response['items'][0]['id']['channelId']
        channel_response = youtube.channels().list(
            part='snippet',
            id=channel_id
        ).execute()

    channel_data = channel_response['items'][0]['snippet']
    
    # Then get recent videos
    videos_response = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        order='date',
        type='video',
        maxResults=5  # Fetch 5 recent videos for testing
    ).execute()

    videos = []
    if videos_response.get('items'):
        for item in videos_response['items']:
            video_data = {
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'publishedAt': item['snippet']['publishedAt']
            }
            videos.append(video_data)

    return {
        'handle': channel['handle'],
        'title': channel_data['title'],
        'description': channel_data['description'],
        'videos': videos,
        'fetched_at': datetime.utcnow().isoformat()
    }

def fetch_video_data(youtube, video: Dict[str, str]) -> Dict[str, Any]:
    """Fetch video data including transcript if available."""
    video_response = youtube.videos().list(
        part='snippet',
        id=video['id']
    ).execute()

    if not video_response.get('items'):
        raise ValueError(f"Video not found: {video['id']}")

    video_data = video_response['items'][0]['snippet']
    
    # Try to fetch transcript
    transcript = None
    transcript_available = False
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video['id'])
        transcript_available = True
    except Exception as e:
        print(f"Could not fetch transcript for {video['id']}: {str(e)}")

    return {
        'id': video['id'],
        'title': video_data['title'],
        'description': video_data['description'],
        'transcript_available': transcript_available,
        'transcript': transcript,
        'thumbnail': video_data['thumbnails']['medium']['url'],
        'publishedAt': video_data['publishedAt'],
        'fetched_at': datetime.utcnow().isoformat()
    }

def main():
    """Main function to fetch and save test data."""
    # Load API key from environment
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY environment variable not set")

    # Initialize YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Load test inputs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    inputs = load_test_inputs(os.path.join(script_dir, 'test_inputs.json'))

    # Fetch data for each channel and video
    test_data = {
        'channels': [],
        'videos': [],
        'generated_at': datetime.utcnow().isoformat()
    }

    # Fetch channel data
    for channel in inputs['channels']:
        try:
            channel_data = fetch_channel_data(youtube, channel)
            test_data['channels'].append(channel_data)
        except Exception as e:
            print(f"Error fetching channel data for {channel['handle']}: {str(e)}")

    # Fetch video data
    for video in inputs['videos']:
        try:
            video_data = fetch_video_data(youtube, video)
            test_data['videos'].append(video_data)
        except Exception as e:
            print(f"Error fetching video data for {video['id']}: {str(e)}")

    # Save test data to JSON file
    output_path = os.path.join(script_dir, 'test_data.json')
    with open(output_path, 'w') as f:
        json.dump(test_data, f, indent=4)
    
    print(f"Test data saved to {output_path}")

if __name__ == '__main__':
    main()
