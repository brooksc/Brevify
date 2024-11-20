# Brevify Project Overview

## Mission
Brevify is a web application designed to transform YouTube channel content into interactive learning experiences. The user journey is streamlined into four simple steps:

1. Load the website
2. Enter a YouTube channel URL
3. Click "Fetch Videos"
4. View a list of all videos from that channel

Each video can be analyzed using your existing AI assistant subscriptions (ChatGPT, Claude) for accelerated learning.

## Core Features

1. Channel URL Processing
   - Simple input field for YouTube channel URLs
   - Support for various channel URL formats
   - Clear error messages for invalid URLs

2. Video List Display
   - Clean grid layout of video cards
   - Thumbnail and basic video information
   - Direct links to AI learning tools

3. AI Tool Integration
   - One-click access to ChatGPT and Claude
   - Automatic transcript loading
   - Learning-focused prompt templates

   ### URL Formats
   The application generates URLs to open transcripts in various AI tools:

   - ChatGPT: `https://chat.openai.com/?model=gpt-4&q=[encoded_prompt]`
   - Claude: `https://claude.ai/chat?prompt=[encoded_prompt]`
   - Gemini: `https://gemini.google.com/?prompt=[encoded_prompt]`

   The prompt is URL-encoded and includes the video transcript along with instructions for analysis.

## Technical Architecture

### Backend Components
- FastHTML for server-side rendering
- YouTube Data API for channel videos
- YouTube Transcript API for subtitles

### Frontend Design
- Minimal, clean interface
- HTMX for dynamic updates
- TailwindCSS for styling

## Non-Goals

To maintain focus and simplicity, the following features are explicitly out of scope:
1. Direct AI API integration 
2. Video downloading or storage
3. Channel management or subscriptions
4. User accounts or authentication
5. Social features or sharing

## Implementation Status

### Completed Features 
- FastHTML application structure
- Channel URL processing
- Video list display
- Basic AI tool integration
- Error handling framework

### Future Enhancements
1. Custom prompt templates
2. User preferences
3. Performance optimization
4. Comprehensive testing
5. Accessibility improvements
