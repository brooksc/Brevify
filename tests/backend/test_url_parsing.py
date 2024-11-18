"""
Test URL parsing functionality.
"""
import pytest
from transcribe import get_video_id, get_channel_id
from tests.data.test_data import get_channel_data, get_video_data

def test_get_video_id_valid_urls():
    """Test video ID extraction from various valid URL formats."""
    video_data = get_video_data('with_transcript')
    video_id = video_data['id']
    
    test_cases = [
        (f'https://www.youtube.com/watch?v={video_id}', video_id),
        (f'https://youtu.be/{video_id}', video_id),
        (f'https://www.youtube.com/watch?v={video_id}&t=123', video_id),
        (f'https://youtube.com/watch?v={video_id}', video_id),
    ]
    for url, expected_id in test_cases:
        assert get_video_id(url) == expected_id

def test_get_video_id_invalid_urls():
    """Test video ID extraction with invalid URLs."""
    invalid_urls = [
        'https://youtube.com',
        'https://youtube.com/watch',
        'https://youtube.com/watch?v=',
        'https://example.com/video',
        '',
        None,
    ]
    for url in invalid_urls:
        with pytest.raises(ValueError):
            get_video_id(url)

def test_get_channel_id_valid_urls(mock_youtube_api):
    """Test channel ID extraction from various valid URL formats."""
    channel_data = get_channel_data('valid_channel')
    channel_id = channel_data['id']
    
    # Mock YouTube API response for channel search
    mock_search = mock_youtube_api.search().list
    mock_search.return_value.execute.return_value = {
        'items': [{'id': {'channelId': channel_id}}]
    }

    test_cases = [
        (f'https://www.youtube.com/channel/{channel_id}', channel_id),
        (f'https://youtube.com/{channel_data["handle"]}', channel_id),
    ]
    for url, expected_id in test_cases:
        assert get_channel_id(url) == expected_id

def test_get_channel_id_invalid_urls(mock_youtube_api):
    """Test channel ID extraction with invalid URLs."""
    # Mock YouTube API response for failed channel search
    mock_search = mock_youtube_api.search().list
    mock_search.return_value.execute.return_value = {'items': []}

    invalid_urls = [
        'https://youtube.com',
        'https://youtube.com/channel',
        'https://youtube.com/channel/',
        'https://example.com/channel',
        '',
        None,
    ]
    for url in invalid_urls:
        with pytest.raises(ValueError):
            get_channel_id(url)
