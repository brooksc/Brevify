"""Main FastAPI application."""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.services.youtube_service import YouTubeService
from app.components.video_list import VideoList
from app.db.database import get_db, create_db_and_tables
from app.models.models import Channel, Video

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get base directory
BASE_DIR = Path(__file__).resolve().parent

# Create FastAPI app
app = FastAPI()

# Mount static directory
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Initialize video list component
video_list = VideoList(templates)

@app.on_event("startup")
async def on_startup():
    """Create database tables on startup."""
    create_db_and_tables()

def get_youtube_service(db: Session = Depends(get_db)) -> YouTubeService:
    """Get YouTubeService instance with database session."""
    return YouTubeService(db)

@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    db: Session = Depends(get_db),
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """Render the main page."""
    # Get all channels and their videos
    channels = db.query(Channel).all()
    videos = []
    for channel in channels:
        channel_videos = await youtube_service.get_videos(channel.id)
        videos.extend(channel_videos)
    
    # Sort by published date
    videos.sort(key=lambda x: x.published_at, reverse=True)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "videos": videos
    })

@app.post("/api/channel")
async def add_channel(
    request: Request,
    channel_url: str = Form(...),
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """Add a new channel and fetch its videos."""
    try:
        # Get or create channel
        channel = await youtube_service.get_channel_info(channel_url)
        if not channel:
            return {"error": "Could not fetch channel info"}
        
        # Fetch videos (this will cache them)
        videos = await youtube_service.get_videos(channel.id)
        
        # Return the video list partial
        return templates.TemplateResponse("video_list.html", {
            "request": request,
            "videos": videos
        })
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        return {"error": str(e)}

@app.get("/api/transcript/{video_id}")
async def get_transcript(
    video_id: str,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """Get transcript for a specific video."""
    transcript = await youtube_service.get_transcript(video_id)
    if transcript:
        return {"transcript": transcript}
    return {"transcript": None}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8888))
    logger.info(f"Starting FastAPI server on port {port}")
    uvicorn.run("main:app", host="localhost", port=port, reload=True)
