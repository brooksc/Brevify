# Features and User Stories

## Core Features

### 1. Channel URL Input
- Text input field for YouTube channel URL
- Support for channel URLs in formats:
  - youtube.com/c/ChannelName
  - youtube.com/channel/ID
  - youtube.com/user/Username
- Real-time validation and error messages
- "Fetch Videos" button with loading state

### 2. Video List Display
- Grid layout of video cards
- Each card shows:
  - Video thumbnail
  - Title
  - Description (truncated)
  - Channel name
  - Publication date
- Responsive design (1-3 columns)
- Loading state while fetching

### 3. AI Tool Integration
- Each video card has:
  - "Open in ChatGPT" button
  - "Open in Claude" button
- Automatic transcript fetching
- Pre-formatted learning prompts

#### Default Prompt Template
```
The following is a transcript from a YouTube video. Please analyze it carefully:

[TRANSCRIPT]

---

Based on this transcript, please provide:

1. Summarize the key points and main ideas (2-3 sentences)
2. List the most important insights or takeaways (3-5 bullet points)
3. Identify any new or interesting concepts that were introduced
4. Note any practical applications or action items
5. Suggest 2-3 related topics I might want to learn about next

Please format your response using markdown, with clear headings for each section.
```

## User Stories

### 1. Channel URL Input
```python
As a user,
I want to paste a YouTube channel URL and click "Fetch Videos"
So that I can see all videos from that channel

Acceptance Criteria:
- Input field accepts all YouTube channel URL formats
- Invalid URLs show clear error messages
- Loading state shown while fetching
- Success/failure feedback provided
```

### 2. Video List Display
```python
As a user,
I want to see a grid of video cards after fetching
So that I can browse the channel's content

Acceptance Criteria:
- Cards show video thumbnails and details
- Grid adjusts to screen size
- Loading states are clear
- Error states are handled gracefully
```

### 3. AI Analysis
```python
As a user,
I want to click an AI tool button on a video
So that I can get AI-powered learning insights

Acceptance Criteria:
- One-click access to AI tools
- Transcript automatically included
- Learning-focused prompt pre-filled
- Clear error handling for missing transcripts
```

## Implementation Details

### 1. URL Processing
```python
@rt('/')
def index():
    """Main page with URL input."""
    return Div(
        H1("Brevify"),
        P("Enter a YouTube channel URL to get started"),
        Form(
            Input(name="url", placeholder="Channel URL"),
            Button("Fetch Videos")
        )
    )
```

### 2. Video List
```python
@rt('/process-channel')
async def process_channel(url: str):
    """Process channel URL and show videos."""
    channel_id = youtube_service.extract_channel_id(url)
    videos = youtube_service.get_channel_videos(channel_id)
    return VideoList(videos)
```

### 3. AI Integration
```python
@rt('/launch-ai/{service}/{video_id}')
async def launch_ai(service: str, video_id: str):
    """Launch AI tool with video transcript."""
    transcript = youtube_service.get_transcript(video_id)
    url = ai_service.get_url(service, transcript)
    return Script(f"window.open('{url}', '_blank')")
```

## Error Handling

### Channel URL Errors
- Invalid URL format
- Channel not found
- API quota exceeded
- Network connectivity issues

### Video List Errors
- Empty channel
- Private videos
- Age-restricted content
- Failed thumbnail loading

### Transcript Errors
- Missing transcripts
- Non-English content
- Manual captions only
- Processing errors

## Success Criteria
1. Channel URL processing works for all formats
2. Video list displays correctly on all devices
3. AI tool integration works reliably
4. Error handling provides clear feedback
