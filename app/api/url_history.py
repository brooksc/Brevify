"""
API endpoints for URL history management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl

from app.database import get_db
from app.services.url_history_service import URLHistoryService

router = APIRouter()

class URLBase(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    tags: Optional[List[str]] = None

class URLResponse(URLBase):
    id: int
    access_count: int
    is_favorite: bool
    created_at: str
    last_accessed: str
    source: str

    class Config:
        orm_mode = True

@router.post("/urls/", response_model=URLResponse)
async def add_url(url_data: URLBase, db: Session = Depends(get_db)):
    """Add a new URL to history."""
    service = URLHistoryService(db)
    url_entry = service.add_url(
        str(url_data.url),
        url_data.title,
        tags=url_data.tags
    )
    return url_entry

@router.get("/urls/recent/", response_model=List[URLResponse])
async def get_recent_urls(limit: int = 10, db: Session = Depends(get_db)):
    """Get recently accessed URLs."""
    service = URLHistoryService(db)
    return service.get_recent_urls(limit)

@router.get("/urls/favorites/", response_model=List[URLResponse])
async def get_favorite_urls(db: Session = Depends(get_db)):
    """Get favorite URLs."""
    service = URLHistoryService(db)
    return service.get_favorite_urls()

@router.post("/urls/{url_id}/favorite/")
async def toggle_favorite(url_id: int, db: Session = Depends(get_db)):
    """Toggle favorite status for a URL."""
    service = URLHistoryService(db)
    is_favorite = service.toggle_favorite(url_id)
    return {"is_favorite": is_favorite}

@router.post("/urls/{url_id}/tags/{tag_name}/")
async def add_tag(url_id: int, tag_name: str, db: Session = Depends(get_db)):
    """Add a tag to a URL."""
    service = URLHistoryService(db)
    success = service.add_tag(url_id, tag_name)
    if not success:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"status": "success"}

@router.delete("/urls/{url_id}/tags/{tag_name}/")
async def remove_tag(url_id: int, tag_name: str, db: Session = Depends(get_db)):
    """Remove a tag from a URL."""
    service = URLHistoryService(db)
    success = service.remove_tag(url_id, tag_name)
    if not success:
        raise HTTPException(status_code=404, detail="URL or tag not found")
    return {"status": "success"}

@router.get("/urls/search/", response_model=List[URLResponse])
async def search_urls(q: str, limit: int = 10, db: Session = Depends(get_db)):
    """Search URLs by title or URL string."""
    service = URLHistoryService(db)
    return service.search_urls(q, limit)

@router.get("/urls/suggestions/", response_model=List[URLResponse])
async def get_url_suggestions(q: str, limit: int = 5, db: Session = Depends(get_db)):
    """Get URL suggestions based on partial input."""
    service = URLHistoryService(db)
    return service.get_url_suggestions(q, limit)
