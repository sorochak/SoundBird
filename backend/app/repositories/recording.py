# backend/app/repositories/recording.py

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.models.recording import Recording
from backend.app.schemas.recording import RecordingStatus

class RecordingRepository:
  def __init__(self, db: Session):
    """
    Initialize the repository with a SQLAlchemy session.
    """
    self.db = db
  
  def create(self, file_name: str, lat: float, lon: float, recording_datetime: datetime) -> Recording:
    """
    Create a new recording with status 'PENDING'.

    Args:
        file_name: Name of the uploaded audio file.
        lat: Latitude of the recording location.
        lon: Longitude of the recording location.
        recording_datetime: Datetime the recording was made.

    Returns:
        The created Recording object with populated ID and timestamps.
    """
    db_recording = Recording(
      file_name=file_name,
      lat=lat,
      lon=lon,
      recording_datetime=recording_datetime,
      status=RecordingStatus.PENDING
    )
    self.db.add(db_recording)
    self.db.commit()
    self.db.refresh(db_recording)
    return db_recording

  def get(self, recording_id: int) -> Optional[Recording]:
    """
    Retrieve a single recording by its ID.

    Args:
        recording_id: Primary key of the recording to fetch.

    Returns:
        The Recording object if found, otherwise None.
    """
    
    return self.db.query(Recording).filter(Recording.id == recording_id).first()
  
  def list(self, skip: int = 0, limit: int = 100) -> List[Recording]:
    """
    Retrieve multiple recordings (for admin or debug purposes).

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        A list of Recording objects.
    """
    return self.db.query(Recording).offset(skip).limit(limit).all()
  
  def update_status(self, recording_id: int, status: RecordingStatus, error_message: Optional[str] = None) -> bool:
    """
    Update the status and optional error message for a recording.

    Args:
        recording_id: Primary key of the recording to update.
        status: New status value ('PROCESSING', 'COMPLETED', or 'FAILED').
        error_message: Optional error message if status is 'FAILED'.

    Returns:
        True if a row was updated, False if no matching recording was found.
    """
    updated_rows = self.db.query(Recording).filter(Recording.id == recording_id).update(
      {"status": status, "error_message": error_message}
    )
    self.db.commit()
    return updated_rows > 0