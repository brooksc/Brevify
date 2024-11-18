"""Test data utilities."""
import json
import os
from typing import Dict, Any

def load_test_data() -> Dict[str, Any]:
    """Load test data from JSON file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, 'test_data_mock.json')
    
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_channel_data(channel_type: str = 'valid_channel') -> Dict[str, str]:
    """Get channel test data."""
    data = load_test_data()
    return data['channels'][channel_type]

def get_video_data(video_type: str = 'with_transcript') -> Dict[str, str]:
    """Get video test data."""
    data = load_test_data()
    return data['videos'][video_type]
