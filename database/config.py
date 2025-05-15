# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

"""
Database Configuration

- Defaults to local SQLite for quick development and testing.
- Supports automatic switch to PostgreSQL when DATABASE_URL is set in the environment.

TODO:
- Set up PostgreSQL database for production.
- Update .env file with the real DATABASE_URL once ready.

Example PostgreSQL URL format:
postgresql+psycopg2://username:password@hostname:port/dbname
"""


# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable, fallback to local SQLite for dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# Dependency to get the database session
def get_db():
    """
    Dependency to get a database session.
    Yields:
        Session: A new database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Note: The get_db function is used in the FastAPI routes to provide a database session for each request.
# This ensures that the session is properly closed after the request is completed.
# This is important for resource management and preventing connection leaks.
# Example usage in a FastAPI route:
# from fastapi import Depends
# from sqlalchemy.orm import Session
# from .database import get_db
# from .models import YourModel
# from .schemas import YourSchema
#
# @router.post("/your-endpoint")
# def create_item(item: YourSchema, db: Session = Depends(get_db)):
#     db_item = YourModel(**item.dict())
#     db.add(db_item)
