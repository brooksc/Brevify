# Brevify: Your Shortcut to YouTube Wisdom

Unlock deeper understanding from YouTube content by seamlessly connecting video transcripts with your preferred AI assistant.

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

- [✓] **Chrome Extension**
  - Seamless integration with AI services
  - Automatic transcript injection
  - Support for multiple AI platforms
  - Easy installation and setup

- [✓] **Modern UI**
  - Responsive design
  - Dark/Light mode
  - Loading states
  - Error handling

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- YouTube Data API key
- Subscription to at least one AI service:
  - OpenAI ChatGPT
  - Anthropic Claude
  - Google Gemini

## Getting Started

### 1. YouTube API Setup

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

### 2. Environment Setup

1. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

2. Add your YouTube API key to the `.env` file:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

### 3. Backend Installation

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
   ./start
   ```
   This will start the server on `http://localhost:8888`

### 4. Chrome Extension Installation

1. Open Google Chrome and navigate to `chrome://extensions`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `extension` directory from the project
4. The Brevify extension icon should appear in your Chrome toolbar

## Usage

1. **Start the Server**
   - Make sure the backend server is running on `localhost:8888`
   - You should see the Brevify web interface when you visit the URL

2. **Enter YouTube URL**
   - Paste any YouTube video URL into the input field
   - The system will fetch the video information and transcript

3. **Analyze with AI**
   - Click on any of the AI assistant buttons (ChatGPT, Claude, or Gemini)
   - The extension will automatically:
     - Open the AI service in a new tab
     - Inject the transcript
     - Apply learning-focused prompts

4. **Review Insights**
   - The AI assistant will analyze the transcript
   - Get detailed insights about the video content
   - Ask follow-up questions for deeper understanding

## Project Structure
```
brevify/
├── app.py              # FastAPI application
├── extension/          # Chrome extension
│   ├── manifest.json   # Extension configuration
│   ├── content.js      # Content script
│   ├── background.js   # Background worker
│   └── ai-service.js   # AI service integration
├── templates/          # HTML templates
├── static/            
│   ├── css/           # Styles
│   └── js/            # Frontend JavaScript
└── requirements.txt    # Python dependencies
```

## Troubleshooting

### Common Issues

1. **Extension Not Detected**
   - Make sure the extension is properly installed
   - Check if it's enabled in Chrome extensions
   - Try reloading the extension
   - Refresh the Brevify webpage

2. **Invalid YouTube URL**
   - Ensure the URL is from youtube.com
   - Check if the video has captions/transcripts

3. **AI Service Issues**
   - Verify you're logged into the AI service
   - Check if the service is accessible in your region
   - Make sure you have an active subscription

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
- Secure extension messaging
