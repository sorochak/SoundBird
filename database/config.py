# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path


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


# Load .env from project root
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Database URL from environment variable, fallback to local SQLite for dev
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Make sure you have a .env file in the project root "
        "and that it contains a valid DATABASE_URL."
    )

print("DATABASE_URL used:",DATABASE_URL)

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
