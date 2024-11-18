"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
from flask import Flask
from transcribe import app as flask_app

@pytest.fixture
def app():
    """Create a Flask test client."""
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client for making requests."""
    return app.test_client()

@pytest.fixture
def mock_youtube_api(mocker):
    """Mock the YouTube Data API responses."""
    mock_build = mocker.patch('transcribe.build')
    mock_youtube = mocker.MagicMock()
    
    # Set up method chains for videos().list().execute()
    mock_videos = mocker.MagicMock()
    mock_videos_list = mocker.MagicMock()
    mock_videos.list.return_value = mock_videos_list
    mock_youtube.videos.return_value = mock_videos
    
    # Set up method chains for channels().list().execute()
    mock_channels = mocker.MagicMock()
    mock_channels_list = mocker.MagicMock()
    mock_channels.list.return_value = mock_channels_list
    mock_youtube.channels.return_value = mock_channels
    
    # Set up method chains for search().list().execute()
    mock_search = mocker.MagicMock()
    mock_search_list = mocker.MagicMock()
    mock_search.list.return_value = mock_search_list
    mock_youtube.search.return_value = mock_search
    
    # Set up list().execute() return values
    mock_videos_list.execute = mocker.MagicMock()
    mock_channels_list.execute = mocker.MagicMock()
    mock_search_list.execute = mocker.MagicMock()
    
    mock_build.return_value = mock_youtube
    return mock_youtube

@pytest.fixture
def mock_transcript_api(mocker):
    """Mock the YouTube Transcript API responses."""
    mock_get_transcript = mocker.patch('transcribe.YouTubeTranscriptApi.get_transcript')
    return mock_get_transcript
