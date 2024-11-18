# Brevify: YouTube Learning Assistant

Transform YouTube videos into quick, insightful learning experiences by leveraging your existing AI subscriptions.

## Overview

Brevify helps you learn faster from YouTube content by seamlessly connecting video transcripts with your preferred AI assistant (ChatGPT, Claude, or Gemini). Instead of paying for additional API access, Brevify lets you use your existing AI subscriptions to analyze video content.

### Core Features

- [✓] **YouTube Integration**
  - Video transcript extraction
  - Metadata fetching
  - Multiple URL format support
  
- [✓] **AI Assistant Integration**
  - ChatGPT support
  - Claude.ai support
  - Gemini support
  - Custom prompt templates

- [✓] **Modern UI**
  - Responsive design
  - Dark/Light mode
  - Loading states
  - Error handling

## Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, or Safari)
- YouTube Data API key
- Subscription to at least one AI service:
  - OpenAI ChatGPT
  - Anthropic Claude
  - Google Gemini

## Getting a YouTube API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your new API key
5. (Optional) Restrict the API key:
   - Click on the newly created API key
   - Under "Application restrictions", choose "HTTP referrers"
   - Under "API restrictions", select "YouTube Data API v3"

## Environment Setup

1. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

2. Add your YouTube API key to the `.env` file:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   FLASK_ENV=development
   FLASK_APP=app.py
   ```

3. (Optional) Add rate limiting settings:
   ```
   YOUTUBE_QUOTA_PER_DAY=10000  # Default YouTube quota
   RATE_LIMIT_PER_MINUTE=60     # API requests per minute
   ```

4. Make sure to add `.env` to your `.gitignore` to keep your API key secure:
   ```bash
   echo ".env" >> .gitignore
   ```

> **Note**: The YouTube API has a daily quota limit. The free tier provides 10,000 units per day. Each API operation costs a different number of units:
> - Video caption retrieval: 50-100 units
> - Video metadata: 1-2 units
> - Channel information: 1-3 units

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/brevify.git
   cd brevify
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the development server:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Enter YouTube URL**
   - Paste any YouTube video URL
   - The system will fetch the transcript and metadata

2. **Choose AI Assistant**
   - Select your preferred AI assistant
   - Each button opens in a new tab with the transcript and prompt

3. **Customize Analysis**
   - Use default prompts or create your own
   - Focus on key points, summaries, or detailed analysis

4. **Review Insights**
   - Get AI-powered analysis of the video content
   - Save or share interesting insights

## Development

### Project Structure
```
brevify/
├── app.py              # Flask application
├── static/            
│   ├── css/           # Tailwind CSS
│   └── js/            # Frontend JavaScript
├── templates/         # HTML templates
├── tests/             # Test suite
└── requirements.txt   # Python dependencies
```

### Running Tests
```bash
pytest
```

### Code Style
- Python: Follow PEP 8
- JavaScript: ESLint configuration
- HTML/CSS: Prettier formatting

## Troubleshooting

### Common Issues

1. **Invalid YouTube URL**
   - Ensure the URL is from youtube.com
   - Check if the video has captions/transcripts

2. **API Key Issues**
   - Verify your YouTube API key is valid
   - Check quota limits

3. **Transcript Not Available**
   - Some videos don't have transcripts
   - Try videos with manual captions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

- No API keys stored on server
- Local storage for settings
- CORS protection enabled
- Input sanitization
