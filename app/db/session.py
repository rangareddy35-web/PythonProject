"""
Database configuration and connection setup for PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using them
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
