"""Database module for storing URLs."""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'brevify.db')

def init_db():
    """Initialize the database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create table for storing URLs
    c.execute('''
        CREATE TABLE IF NOT EXISTS saved_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_url(url: str) -> bool:
    """Save a URL to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO saved_urls (url) VALUES (?)', (url,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving URL: {e}")
        return False

def get_saved_urls() -> list:
    """Get all saved URLs, ordered by most recent first."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT url FROM saved_urls ORDER BY created_at DESC')
        urls = [row[0] for row in c.fetchall()]
        conn.close()
        return urls
    except Exception as e:
        print(f"Error getting URLs: {e}")
        return []
