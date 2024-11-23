"""
URL History models for storing and managing user's video and channel URLs.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for URL tags
url_tags = Table(
    'url_tags',
    Base.metadata,
    Column('url_id', Integer, ForeignKey('url_history.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class URLHistory(Base):
    """Model for storing URL history entries."""
    __tablename__ = 'url_history'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=1)
    is_favorite = Column(Boolean, default=False)
    source = Column(String, default='manual')  # manual, shared, extension
    
    # Relationships
    tags = relationship('Tag', secondary=url_tags, back_populates='urls')

    def __repr__(self):
        return f"<URLHistory(url='{self.url}', title='{self.title}', access_count={self.access_count})>"

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count,
            'is_favorite': self.is_favorite,
            'source': self.source,
            'tags': [tag.name for tag in self.tags]
        }

class Tag(Base):
    """Model for URL tags."""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    
    # Relationships
    urls = relationship('URLHistory', secondary=url_tags, back_populates='tags')

    def __repr__(self):
        return f"<Tag(name='{self.name}')>"
