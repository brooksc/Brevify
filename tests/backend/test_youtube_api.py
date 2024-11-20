"""
Test YouTube API integration.
"""
from unittest.mock import patch, MagicMock
import pytest
from youtube_transcript_api import TranscriptsDisabled
from googleapiclient.errors import HttpError

from tests.data.test_data import get_channel_data, get_video_data
from transcribe import fetch_transcript, fetch_channel_videos, get_channel_id

@patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript')
def test_fetch_transcript_success(mock_transcript_api):
    """Test successful transcript fetching."""
    video_data = get_video_data('with_transcript')
    mock_transcript = [{'text': 'Test transcript', 'start': 0.0, 'duration': 1.0}]
    mock_transcript_api.return_value = mock_transcript
    
    result = fetch_transcript(video_data['id'])
    assert result['success'] is True
    assert result['transcript'] == mock_transcript

@patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript')
def test_fetch_transcript_failure(mock_transcript_api):
    """Test transcript fetching failure."""
    video_data = get_video_data('no_transcript')
    mock_transcript_api.side_effect = TranscriptsDisabled('No transcript available')
    
    with pytest.raises(ValueError) as exc_info:
        fetch_transcript(video_data['id'])
    assert str(exc_info.value) == 'No transcript available'

@patch('transcribe.build')
def test_fetch_channel_videos_success(mock_build):
    """Test successful channel videos fetching."""
    channel_data = get_channel_data('valid_channel')
    video_data = get_video_data('with_transcript')

    # Mock channel lookup response
    mock_channel_response = {
        'items': [{
            'id': channel_data['id'],
            'snippet': {
                'title': channel_data['title']
            }
        }]
    }

    # Mock videos response with exactly one video
    mock_videos_response = {
        'items': [
            {
                'id': {'videoId': video_data['id']},
                'snippet': {
                    'title': video_data['title'],
                    'description': video_data['description'],
                    'thumbnails': {'medium': {'url': video_data['thumbnail_url']}},
                    'publishedAt': video_data['published_at']
                }
            }
        ]
    }

    # Set up mock API
    mock_youtube = MagicMock()
    mock_channels = MagicMock()
    mock_search = MagicMock()
    
    mock_youtube.channels.return_value = mock_channels
    mock_youtube.search.return_value = mock_search
    
    mock_channel_list = MagicMock()
    mock_search_list = MagicMock()
    
    mock_channels.list.return_value = mock_channel_list
    mock_search.list.return_value = mock_search_list
    
    mock_channel_list.execute.return_value = mock_channel_response
    mock_search_list.execute.return_value = mock_videos_response
    
    mock_build.return_value = mock_youtube

    result = fetch_channel_videos(channel_data['id'])

    # Verify channel lookup was called correctly
    mock_channels.list.assert_called_once_with(
        part='snippet',
        id=channel_data['id']
    )

    # Verify video search was called correctly
    mock_search.list.assert_called_once_with(
        part='snippet',
        channelId=channel_data['id'],
        order='date',
        type='video',
        maxResults=10
    )

    assert result['success'] is True
    assert result['channel_title'] == channel_data['title']
    assert len(result['videos']) == 1
    assert result['videos'][0]['id'] == video_data['id']

@patch('transcribe.build')
def test_fetch_channel_videos_no_videos(mock_build):
    """Test channel fetching with no videos."""
    channel_data = get_channel_data('no_videos_channel')

    # Mock channel lookup response
    mock_channel_response = {
        'items': [{
            'id': channel_data['id'],
            'snippet': {
                'title': channel_data['title']
            }
        }]
    }

    # Mock empty videos response
    mock_videos_response = {'items': []}

    # Set up mock API
    mock_youtube = MagicMock()
    mock_channels = MagicMock()
    mock_search = MagicMock()
    
    mock_youtube.channels.return_value = mock_channels
    mock_youtube.search.return_value = mock_search
    
    mock_channel_list = MagicMock()
    mock_search_list = MagicMock()
    
    mock_channels.list.return_value = mock_channel_list
    mock_search.list.return_value = mock_search_list
    
    mock_channel_list.execute.return_value = mock_channel_response
    mock_search_list.execute.return_value = mock_videos_response
    
    mock_build.return_value = mock_youtube

    result = fetch_channel_videos(channel_data['id'])

    assert result['success'] is True
    assert result['channel_title'] == channel_data['title']
    assert len(result['videos']) == 0

@patch('transcribe.build')
def test_fetch_channel_videos_channel_not_found(mock_build):
    """Test channel not found error."""
    # Mock empty channel response
    mock_channel_response = {'items': []}

    # Set up mock API
    mock_youtube = MagicMock()
    mock_channels = MagicMock()
    mock_youtube.channels.return_value = mock_channels
    mock_channel_list = MagicMock()
    mock_channels.list.return_value = mock_channel_list
    mock_channel_list.execute.return_value = mock_channel_response
    mock_build.return_value = mock_youtube

    with pytest.raises(ValueError) as exc_info:
        fetch_channel_videos('invalid_channel_id')
    assert 'Channel not found' in str(exc_info.value)

@patch('transcribe.build')
def test_fetch_channel_videos_api_error(mock_build):
    """Test YouTube API error handling."""
    mock_build.side_effect = HttpError(
        resp=MagicMock(status=403),
        content=b'API quota exceeded'
    )

    with pytest.raises(ValueError) as exc_info:
        fetch_channel_videos('any_channel_id')
    assert 'Error fetching channel data' in str(exc_info.value)

def test_get_channel_id_valid_urls():
    """Test channel ID extraction from various valid URL formats."""
    test_cases = [
        ('https://www.youtube.com/channel/UC1234567890', 'UC1234567890'),
        ('https://www.youtube.com/@handle', '@handle'),
        ('https://www.youtube.com/c/customurl', 'c/customurl')
    ]
    for url, expected_id in test_cases:
        assert get_channel_id(url) == expected_id

def test_get_channel_id_invalid_urls():
    """Test channel ID extraction with invalid URLs."""
    invalid_urls = [
        'https://www.youtube.com/watch?v=123456',
        'https://www.youtube.com/playlist?list=123456',
        'https://www.google.com',
        'not_a_url'
    ]
    for url in invalid_urls:
        with pytest.raises(ValueError) as exc_info:
            get_channel_id(url)
        assert 'Invalid YouTube URL' in str(exc_info.value)
