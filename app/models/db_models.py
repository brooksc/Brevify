"""Database models for the application."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Channel(Base):
    """YouTube channel model."""
    __tablename__ = "channels"

    id = Column(String, primary_key=True)  # YouTube channel ID
    title = Column(String)
    description = Column(Text)
    thumbnail_url = Column(String)
    url = Column(String)
    last_fetched = Column(DateTime, default=datetime.utcnow)

class Video(Base):
    """YouTube video model."""
    __tablename__ = "videos"

    id = Column(String, primary_key=True)  # YouTube video ID
    channel_id = Column(String, ForeignKey("channels.id"))
    title = Column(String)
    description = Column(Text)
    thumbnail_url = Column(String)
    published_at = Column(DateTime)
    url = Column(String)
    transcript = Column(Text, nullable=True)
    transcript_fetched = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
