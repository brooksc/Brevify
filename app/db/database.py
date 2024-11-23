"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Create database URL
DATABASE_URL = f"sqlite:///{BASE_DIR}/brevify.db"

# Create engine
engine = create_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
from app.models.db_models import Base
Base.metadata.create_all(bind=engine)
