"""Service for managing saved URLs."""
import sqlite3
import os
from pathlib import Path
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class URLService:
    """Service for managing saved URLs."""
    
    def __init__(self):
        """Initialize the URL service."""
        self.db_path = Path(__file__).parent.parent.parent / 'data' / 'brevify.db'
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the database."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            
            # Keep existing saved_urls table
            c.execute('''
                CREATE TABLE IF NOT EXISTS saved_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add new table for channel metadata
            c.execute('''
                CREATE TABLE IF NOT EXISTS channel_metadata (
                    url TEXT PRIMARY KEY,
                    channel_name TEXT,
                    last_video_title TEXT,
                    last_video_date TEXT,
                    last_checked TEXT,
                    FOREIGN KEY (url) REFERENCES saved_urls(url)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_url(self, url: str, channel_info: Dict = None) -> bool:
        """Save a URL and optionally its channel information."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            
            # First check if URL exists
            c.execute('SELECT url FROM saved_urls WHERE url = ?', (url,))
            existing = c.fetchone()
            
            if not existing:
                # Save URL to existing table only if it's new
                c.execute('INSERT INTO saved_urls (url) VALUES (?)', (url,))
            
            # Save or update channel metadata if provided
            if channel_info:
                now = datetime.now().isoformat()
                c.execute('''
                    INSERT OR REPLACE INTO channel_metadata 
                    (url, channel_name, last_video_title, last_video_date, last_checked)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    url,
                    channel_info.get('channel_name', ''),
                    channel_info.get('last_video_title', ''),
                    channel_info.get('last_video_date', ''),
                    now
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving URL: {e}")
            return False
    
    def get_saved_channels(self) -> List[Dict]:
        """Get all saved channels with their information."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            
            # Join saved_urls with channel_metadata to get all information
            # Use DISTINCT to ensure no duplicates
            c.execute('''
                SELECT DISTINCT u.url, m.channel_name, m.last_video_title, m.last_video_date, m.last_checked, u.created_at
                FROM saved_urls u
                LEFT JOIN channel_metadata m ON u.url = m.url
                ORDER BY m.last_video_date DESC NULLS LAST, u.created_at DESC
            ''')
            
            channels = []
            seen_urls = set()  # Track seen URLs to prevent duplicates
            
            for row in c.fetchall():
                url = row[0]
                if url not in seen_urls:  # Only add if URL not seen before
                    seen_urls.add(url)
                    channels.append({
                        'url': url,
                        'channel_name': row[1],
                        'last_video_title': row[2],
                        'last_video_date': row[3],
                        'last_checked': row[4],
                        'created_at': row[5]
                    })
            
            conn.close()
            return channels
        except Exception as e:
            logger.error(f"Error getting channels: {e}")
            return []
