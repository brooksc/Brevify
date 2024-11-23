"""
Service for managing URL history operations.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.url_history import URLHistory, Tag

class URLHistoryService:
    def __init__(self, db: Session):
        self.db = db

    def add_url(self, url: str, title: Optional[str] = None, source: str = 'manual', tags: List[str] = None) -> URLHistory:
        """Add a new URL to history or update existing one."""
        # Check if URL already exists
        url_entry = self.db.query(URLHistory).filter(URLHistory.url == url).first()
        
        if url_entry:
            # Update existing entry
            url_entry.last_accessed = datetime.utcnow()
            url_entry.access_count += 1
            if title:
                url_entry.title = title
        else:
            # Create new entry
            url_entry = URLHistory(
                url=url,
                title=title,
                source=source
            )
            self.db.add(url_entry)

        # Handle tags
        if tags:
            for tag_name in tags:
                tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.db.add(tag)
                if tag not in url_entry.tags:
                    url_entry.tags.append(tag)

        self.db.commit()
        return url_entry

    def get_recent_urls(self, limit: int = 10) -> List[URLHistory]:
        """Get most recently accessed URLs."""
        return self.db.query(URLHistory)\
            .order_by(desc(URLHistory.last_accessed))\
            .limit(limit)\
            .all()

    def get_favorite_urls(self) -> List[URLHistory]:
        """Get favorite URLs."""
        return self.db.query(URLHistory)\
            .filter(URLHistory.is_favorite == True)\
            .order_by(desc(URLHistory.last_accessed))\
            .all()

    def toggle_favorite(self, url_id: int) -> bool:
        """Toggle favorite status for a URL."""
        url_entry = self.db.query(URLHistory).filter(URLHistory.id == url_id).first()
        if url_entry:
            url_entry.is_favorite = not url_entry.is_favorite
            self.db.commit()
            return url_entry.is_favorite
        return False

    def add_tag(self, url_id: int, tag_name: str) -> bool:
        """Add a tag to a URL."""
        url_entry = self.db.query(URLHistory).filter(URLHistory.id == url_id).first()
        if not url_entry:
            return False

        tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            self.db.add(tag)

        if tag not in url_entry.tags:
            url_entry.tags.append(tag)
            self.db.commit()
        return True

    def remove_tag(self, url_id: int, tag_name: str) -> bool:
        """Remove a tag from a URL."""
        url_entry = self.db.query(URLHistory).filter(URLHistory.id == url_id).first()
        if not url_entry:
            return False

        tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
        if tag and tag in url_entry.tags:
            url_entry.tags.remove(tag)
            self.db.commit()
            return True
        return False

    def search_urls(self, query: str, limit: int = 10) -> List[URLHistory]:
        """Search URLs by title or URL string."""
        return self.db.query(URLHistory)\
            .filter(
                (URLHistory.url.ilike(f'%{query}%')) |
                (URLHistory.title.ilike(f'%{query}%'))
            )\
            .order_by(desc(URLHistory.last_accessed))\
            .limit(limit)\
            .all()

    def get_url_suggestions(self, partial_url: str, limit: int = 5) -> List[URLHistory]:
        """Get URL suggestions based on partial input."""
        return self.db.query(URLHistory)\
            .filter(URLHistory.url.ilike(f'%{partial_url}%'))\
            .order_by(desc(URLHistory.access_count))\
            .limit(limit)\
            .all()

    def cleanup_old_entries(self, days: int = 30) -> int:
        """Remove entries older than specified days that aren't favorites."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = self.db.query(URLHistory)\
            .filter(
                URLHistory.last_accessed < cutoff_date,
                URLHistory.is_favorite == False
            )\
            .delete()
        self.db.commit()
        return deleted
