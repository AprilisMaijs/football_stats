from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import os

# Get absolute path to src directory
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define database file location relative to src directory
DATABASE_PATH = os.path.join(SRC_DIR, "football_stats.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine
engine = create_engine(DATABASE_URL)

# SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from .models import Base
    Base.metadata.create_all(bind=engine)

# Optional: Add function to check database existence
def database_exists():
    """Check if database file exists"""
    return os.path.exists(DATABASE_PATH)