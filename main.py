"""Main application module."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.youtube_service import YouTubeService
from app.services.ai_url_service import AIURLService
from app.components.video_list import VideoList

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check required environment variables
if not os.getenv('YOUTUBE_API_KEY'):
    logger.error("YOUTUBE_API_KEY environment variable not set")
    raise ValueError("YOUTUBE_API_KEY environment variable not set")

# Initialize FastAPI app
app = FastAPI(title="Brevify")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Initialize services
youtube_service = YouTubeService()
ai_url_service = AIURLService()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/fetch-videos")
async def fetch_videos(channel_url: str = Form(...)):
    """Fetch videos from a YouTube channel."""
    logger.debug(f"Received channel URL: {channel_url}")
    
    if not channel_url:
        logger.error("No channel URL provided")
        return {"error": "Please provide a YouTube channel URL"}, 400
    
    try:
        # Get videos from channel
        logger.debug("Fetching videos from channel...")
        videos = youtube_service.get_channel_videos(channel_url)
        logger.debug(f"Found {len(videos)} videos")
        
        # Add AI URLs to each video
        for video in videos:
            if video.transcript:
                logger.debug(f"Generating AI URLs for video {video.id}")
                video.chatgpt_url = ai_url_service.get_chatgpt_url(video.transcript)
                video.claude_url = ai_url_service.get_claude_url(video.transcript)
                video.gemini_url = ai_url_service.get_gemini_url(video.transcript)
        
        # Render video list
        logger.debug("Rendering video list...")
        video_list = VideoList(videos)
        html = video_list.render()
        logger.debug("Video list rendered successfully")
        return HTMLResponse(content=html)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {"error": str(e)}, 400

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8888))
    logger.info(f"Starting FastAPI server on port {port}")
    uvicorn.run("main:app", host="localhost", port=port, reload=True)
