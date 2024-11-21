# Brevify Chrome Extension Specification

## Overview
The Brevify Chrome Extension enhances YouTube viewing by providing direct access to AI-powered learning tools. It integrates with the Brevify backend service to analyze video transcripts and generate AI tool links.

## Features
1. Video Page Integration
   - Adds a "Learn with AI" button below YouTube videos
   - Shows AI tool options when transcript is available:
     - ChatGPT Analysis
     - Claude Analysis
     - Gemini Analysis

2. Channel Page Integration
   - Adds "Analyze Channel" button on YouTube channel pages
   - Quick access to Brevify analysis for entire channels

3. UI Components
   - Custom button with Brevify branding
   - Dropdown menu for AI tool selection
   - Loading states and error handling
   - Dark mode support

## Technical Requirements

### Manifest (manifest.json)
```json
{
  "manifest_version": 3,
  "name": "Brevify - AI Learning Assistant",
  "version": "1.0.0",
  "description": "Transform YouTube videos into interactive learning experiences with AI-powered analysis",
  "permissions": [
    "activeTab",
    "storage"
  ],
  "host_permissions": [
    "*://*.youtube.com/*"
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "content_scripts": [
    {
      "matches": ["*://*.youtube.com/*"],
      "js": ["content.js"],
      "css": ["styles.css"]
    }
  ]
}
```

### File Structure
```
extension/
├── manifest.json
├── popup.html
├── popup.js
├── content.js
├── styles.css
├── background.js
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### Integration Points
1. YouTube Video Page
   - Inject button below video player
   - Extract video ID and check for transcript
   - Send requests to Brevify backend

2. YouTube Channel Page
   - Add channel analysis button
   - Extract channel ID/URL
   - Redirect to Brevify web interface

### API Integration
- Backend Endpoint: `http://localhost:8888`
- Endpoints Used:
  - `/fetch-videos` - Get channel videos
  - `/check-transcript` - Check transcript availability

### UI/UX Guidelines
1. Button Styling
   - Match YouTube's design language
   - Use Brevify brand colors
   - Support dark/light themes

2. Loading States
   - Show spinner during API calls
   - Disable buttons when processing
   - Clear error messaging

3. Error Handling
   - Network error recovery
   - Missing transcript messaging
   - User-friendly error displays

### Security Considerations
1. Content Security Policy
2. API Key handling
3. Cross-origin request handling
4. User data protection

## Development Guidelines
1. Use Modern JavaScript (ES6+)
2. Follow Chrome Extension best practices
3. Implement proper error handling
4. Support offline functionality
5. Maintain code documentation

## Testing Requirements
1. Unit tests for core functionality
2. Integration tests with YouTube
3. Cross-browser compatibility
4. Performance testing
5. Security testing