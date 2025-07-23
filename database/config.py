# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path


"""
Database Configuration

- Connects to the database specified in the DATABASE_URL environment variable.
- Raises an error if DATABASE_URL is not set.

To use PostgreSQL, set DATABASE_URL in the .env file using this format:
postgresql+psycopg2://username:password@hostname:port/dbname

Example .env entry:
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/soundbird

"""


# Load .env from project root
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Load DATABASE_URL from environment; required for all environments
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Make sure you have a .env file in the project root "
        "and that it contains a valid DATABASE_URL."
    )

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

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
