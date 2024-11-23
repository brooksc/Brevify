"""SQLModel models for the application."""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class VideoBase(SQLModel):
    """Base model for Video."""
    title: str = Field(index=True)
    description: str
    thumbnail_url: str
    url: str
    published_at: datetime
    channel_id: str = Field(foreign_key="channel.id")

class Video(VideoBase, table=True):
    """Video model with database fields."""
    id: str = Field(primary_key=True)  # YouTube video ID
    transcript: Optional[str] = None
    transcript_fetched: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    channel: "Channel" = Relationship(back_populates="videos")

class Channel(SQLModel, table=True):
    """YouTube channel model."""
    id: str = Field(primary_key=True)  # YouTube channel ID
    title: str = Field(index=True)
    description: str
    thumbnail_url: str
    url: str
    last_fetched: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    videos: list[Video] = Relationship(back_populates="channel")
