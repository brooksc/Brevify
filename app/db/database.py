"""Database connection and session management using SQLModel."""
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine
from app.models.models import Channel, Video

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Create database URL
DATABASE_URL = f"sqlite:///{BASE_DIR}/brevify.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)

def get_db():
    """Get database session."""
    with Session(engine) as session:
        yield session
