"""
Test Flask API endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock
from transcribe import app, cache
from tests.data.test_data import get_channel_data, get_video_data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test"""
    cache.clear()

def test_index_route(client):
    """Test the index route returns the main page"""
    response = client.get('/')
    assert response.status_code == 200

def test_transcript_no_url(client):
    """Test transcript endpoint with no URL"""
    response = client.get('/api/transcript')
    assert response.status_code == 400
    assert response.json['error'] == 'No URL provided'

def test_transcript_invalid_url(client):
    """Test transcript endpoint with invalid URL"""
    response = client.get('/api/transcript?url=invalid')
    assert response.status_code == 400
    assert 'Invalid YouTube URL' in response.json['error']

@patch('transcribe.YouTubeTranscriptApi')
@patch('transcribe.build')
def test_transcript_success(mock_build, mock_transcript_api, client):
    """Test successful transcript fetch"""
    video_data = get_video_data('with_transcript')
    # Mock YouTube API response
    mock_video = {
        'items': [{
            'snippet': {
                'title': video_data['title']
            }
        }]
    }
    mock_youtube = MagicMock()
    mock_youtube.videos().list().execute.return_value = mock_video
    mock_build.return_value = mock_youtube

    mock_transcript = [{'text': 'Test', 'start': 0.0}]
    mock_transcript_api.get_transcript.return_value = mock_transcript

    response = client.get(f'/api/transcript?url=https://www.youtube.com/watch?v={video_data["id"]}')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['transcript'] == mock_transcript

@patch('transcribe.YouTubeTranscriptApi')
def test_transcript_not_available(mock_transcript_api, client):
    """Test transcript not available"""
    video_data = get_video_data('no_transcript')
    mock_transcript_api.get_transcript.side_effect = Exception('No transcript available')
    response = client.get(f'/api/transcript?url=https://www.youtube.com/watch?v={video_data["id"]}')
    assert response.status_code == 400
    assert 'No transcript available' in response.json['error']

def test_videos_no_url(client):
    """Test videos endpoint with no URL"""
    response = client.get('/api/videos')
    assert response.status_code == 400
    assert response.json['error'] == 'No URL provided'

def test_videos_invalid_url(client):
    """Test videos endpoint with invalid URL"""
    response = client.get('/api/videos?url=invalid')
    assert response.status_code == 400
    assert 'Invalid YouTube URL' in response.json['error']

@patch('transcribe.build')
def test_videos_success(mock_build, client):
    """Test successful videos fetch"""
    channel_data = get_channel_data('valid_channel')
    video_data = get_video_data('with_transcript')
    
    # Mock YouTube API responses
    mock_channel = {
        'items': [{
            'snippet': {
                'title': channel_data['title']
            }
        }]
    }
    mock_videos = {
        'items': [{
            'id': {'videoId': video_data['id']},
            'snippet': {
                'title': video_data['title'],
                'description': video_data['description'],
                'thumbnails': {
                    'medium': {'url': video_data['thumbnail_url']}
                },
                'publishedAt': video_data['published_at']
            }
        }]
    }
    mock_search = {
        'items': [{
            'id': {'channelId': channel_data['id']}
        }]
    }
    mock_youtube = MagicMock()
    mock_youtube.channels().list().execute.return_value = mock_channel
    mock_youtube.search().list().execute.side_effect = [mock_search, mock_videos]
    mock_build.return_value = mock_youtube

    response = client.get(f'/api/videos?url=https://www.youtube.com/{channel_data["handle"]}')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['channel_title'] == channel_data['title']
    assert len(response.json['videos']) == 1
    assert response.json['videos'][0]['title'] == video_data['title']

@patch('transcribe.build')
def test_videos_channel_not_found(mock_build, client):
    """Test channel not found"""
    mock_youtube = MagicMock()
    mock_youtube.channels().list().execute.return_value = {'items': []}
    mock_build.return_value = mock_youtube

    response = client.get('/api/videos?url=https://www.youtube.com/@nonexistent')
    assert response.status_code == 404
    assert response.json['error'] == 'Channel not found'

@patch('transcribe.build')
def test_videos_no_videos(mock_build, client):
    """Test channel with no videos"""
    channel_data = get_channel_data('no_videos_channel')
    
    # Mock YouTube API responses
    mock_channel = {
        'items': [{
            'snippet': {
                'title': channel_data['title']
            }
        }]
    }
    mock_videos = {
        'items': []
    }
    mock_search = {
        'items': [{
            'id': {'channelId': channel_data['id']}
        }]
    }
    mock_youtube = MagicMock()
    mock_youtube.channels().list().execute.return_value = mock_channel
    mock_youtube.search().list().execute.side_effect = [mock_search, mock_videos]
    mock_build.return_value = mock_youtube

    response = client.get(f'/api/videos?url=https://www.youtube.com/{channel_data["handle"]}')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['channel_title'] == channel_data['title']
    assert len(response.json['videos']) == 0

def test_cache_behavior(client):
    """Test that responses are cached"""
    with patch('transcribe.fetch_transcript') as mock_fetch:
        mock_fetch.return_value = {'success': True, 'transcript': []}
        
        # First request should call the function
        client.get('/api/transcript?url=https://www.youtube.com/watch?v=test123')
        assert mock_fetch.call_count == 1
        
        # Second request should use cache
        client.get('/api/transcript?url=https://www.youtube.com/watch?v=test123')
        assert mock_fetch.call_count == 1

if __name__ == '__main__':
    pytest.main(['-v', __file__])
