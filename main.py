"""Main application module."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.services.youtube_service import YouTubeService
from app.services.ai_url_service import AIURLService
from app.services.url_service import URLService
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

# Get base directory
BASE_DIR = Path(__file__).resolve().parent

# Initialize FastAPI app
app = FastAPI(title="Brevify")

# Mount static directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Set up templates directory
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Initialize services
youtube_service = YouTubeService()
ai_url_service = AIURLService()
url_service = URLService()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page."""
    saved_channels = url_service.get_saved_channels()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "saved_channels": saved_channels
    })

@app.post("/save-url")
async def save_url(channel_url: str = Form(...)):
    """Save a channel URL."""
    if not channel_url:
        return {"error": "Please provide a YouTube channel URL"}
    
    try:
        # Get channel information from YouTube
        channel_info = await youtube_service.get_channel_info(channel_url)
        if url_service.save_url(channel_url, channel_info):
            return {"success": True}
    except Exception as e:
        logger.error(f"Error saving channel: {e}")
        # Still try to save just the URL if channel info fails
        if url_service.save_url(channel_url):
            return {"success": True}
    
    return {"error": "Failed to save URL"}

@app.post("/fetch-videos")
async def fetch_videos(request: Request, channel_url: str = Form(...)):
    """Fetch videos from a YouTube channel."""
    logger.debug(f"Received channel URL: {channel_url}")
    
    if not channel_url:
        return {"error": "Please provide a YouTube channel URL"}
    
    try:
        # Get channel information and save it
        channel_info = await youtube_service.get_channel_info(channel_url)
        url_service.save_url(channel_url, channel_info)
        
        # Get video list and process it through the component
        videos = youtube_service.get_channel_videos(channel_url)
        video_list = VideoList(videos=videos)
        processed_videos = video_list.process_videos()  # This will add AI URLs
        
        # Render using the template
        return templates.TemplateResponse("video_list.html", {
            "request": request,
            "videos": processed_videos
        })
    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8888))
    logger.info(f"Starting FastAPI server on port {port}")
    uvicorn.run("main:app", host="localhost", port=port, reload=True)
