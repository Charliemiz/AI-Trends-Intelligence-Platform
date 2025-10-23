import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_ENV = BASE_DIR.parent / "frontend" / ".env"

load_dotenv(BASE_DIR / ".env")
load_dotenv(FRONTEND_ENV, override=False)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in environment variables")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Create declarative base for models
Base = declarative_base()

# Dependency for FastAPI endpoints
def get_db():
    """
    Creates a new database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()