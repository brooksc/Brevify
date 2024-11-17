# YouTube Video Summary Assistant

A powerful web application that helps you generate AI-powered summaries of YouTube videos using multiple AI services.

## Features

- **Channel URL Support**

  - Standard channel URLs (youtube.com/channel/[ID])
  - Custom URLs (youtube.com/c/[name])
  - Handle URLs (youtube.com/@[handle])

- **API Key Management**

  - Secure storage in localStorage (encrypted)
  - Key validation
  - Easy key management

- **Channel History**

  - Track last 20 channels
  - Store metadata (URL, name, last accessed, video count)
  - Quick channel selection

- **Video Display**

  - Responsive card layout
  - High-quality thumbnails
  - Video metadata (duration, views, upload date)
  - Expandable descriptions
  - Tag display

- **AI Integration**

  - Support for multiple AI services:
    - ChatGPT
    - Claude.ai
    - Gemini
  - Custom prompt templates
  - Batch processing

- **Debug System**
  - Comprehensive logging
  - Log filtering and search
  - Export capabilities
  - Visual state tracking

## Getting Started

1. Clone the repository
2. Open `index.html` in your browser
3. Enter your YouTube API key
4. Start summarizing videos!

## Usage

1. **Enter YouTube API Key**

   - Get an API key from [Google Cloud Console](https://console.cloud.google.com)
   - Enter it in the API key field
   - Test the key using the "Test Key" button

2. **Enter Channel URL**

   - Paste a YouTube channel URL
   - Supports multiple URL formats
   - Recent channels are saved for quick access

3. **Select Videos**

   - Browse through the channel's videos
   - Click "Generate Summary" on videos you want to analyze
   - Track processing status with visual indicators

4. **Configure AI Services**

   - Choose which AI services to use
   - Customize prompt templates
   - View summaries in your preferred AI interface

5. **Debug Panel**
   - Toggle the debug panel for detailed logs
   - Filter and search through logs
   - Export logs for troubleshooting

## Development

Built with:

- HTMX for dynamic interactions
- Tailwind CSS for styling
- Vanilla JavaScript for core functionality
- LocalStorage for data persistence

## License

This project is licensed under the MIT License - see the LICENSE file for details.
