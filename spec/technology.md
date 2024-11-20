# Technology Stack

## Core Technologies

### Frontend
- FastHTML for server-side rendering
- HTMX for dynamic interactions
- TailwindCSS for styling
- No client-side JavaScript

### Backend
- Python 3.9+
- FastHTML framework
- YouTube Data API v3
- YouTube Transcript API

## External APIs

### YouTube APIs
1. Data API v3
   - Channel information retrieval
   - Video list fetching
   - Metadata access
   - Quota management

2. Transcript API
   - Subtitle extraction
   - Language support
   - Error handling

### AI Services
1. ChatGPT
   - URL-based integration
   - Prompt formatting
   - Context management

2. Claude
   - URL-based integration
   - Prompt formatting
   - Context management

## Development Tools

### Required
- Python 3.9+
- pip/conda for package management
- YouTube API credentials
- Git for version control

### Optional
- VS Code with Python extensions
- Postman for API testing
- Chrome DevTools

## Dependencies

### Python Packages
```
fasthtml>=1.0.0
google-api-python-client>=2.0.0
youtube-transcript-api>=0.6.0
python-dotenv>=1.0.0
httpx>=0.24.0
```

### Frontend Assets
```
tailwindcss (CDN)
htmx (CDN)
```

## Configuration

### Environment Variables
```
YOUTUBE_API_KEY=your_api_key
PORT=8888
DEBUG=True
```

### API Configuration
```python
YOUTUBE_API_CONFIG = {
    "api_service_name": "youtube",
    "api_version": "v3",
    "max_results": 50
}
```

## Development Setup

### Local Environment
```bash
# Create conda environment
conda create -n brevify python=3.9
conda activate brevify

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export YOUTUBE_API_KEY=your_key
```

### Running the App
```bash
python main.py
```

## Testing

### Unit Tests
- Component rendering
- URL processing
- API integration
- Error handling

### Integration Tests
- Channel processing
- Video list display
- Transcript fetching
- AI URL generation

## Deployment

### Requirements
- Python 3.9+ runtime
- Environment variables
- API credentials
- Network access

### Process
1. Clone repository
2. Install dependencies
3. Set environment variables
4. Run application

## Performance

### Optimization
- Server-side rendering
- CDN for static assets
- Response caching
- Lazy loading

### Monitoring
- Response times
- API quotas
- Error rates
- Usage metrics
