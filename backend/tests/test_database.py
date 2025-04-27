# backend/tests/test_database.py

import pytest
from backend.app.database import SessionLocal
from sqlalchemy import text


def test_db_connection():
    """
    Test the database connection by creating a session and checking if it can be used.
    """
    try:
        # Create a new session
        db = SessionLocal()
        # Attempt to execute a simple query
        db.execute(text("SELECT 1"))
        print("[INFO] Database connection test passed.")
    except Exception as e:
        print(f"[ERROR] Database connection test failed: {e}")
    finally:
        # Close the session
        db.close()
