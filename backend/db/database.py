"""Database engine, session factory and helper generator.

This module configures the SQLAlchemy engine using the application
configuration, exposes the declarative base for models, and provides a
``get_db`` generator for FastAPI dependency injection.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True) # type: ignore
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Yield a database session and ensure it is closed afterwards.

    Use this function as a FastAPI dependency (``Depends(get_db)``).

    :yields: A SQLAlchemy ``Session`` object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()