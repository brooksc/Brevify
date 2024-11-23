"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path

# Create data directory if it doesn't exist
data_dir = Path(__file__).parent.parent / 'data'
data_dir.mkdir(exist_ok=True)

# Database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{data_dir}/brevify.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database."""
    from app.models.url_history import Base
    Base.metadata.create_all(bind=engine)
