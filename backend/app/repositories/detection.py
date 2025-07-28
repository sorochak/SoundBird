# backend/app/repositories/detection.py

from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from datetime import datetime

from backend.app.models.detection import Detections
from backend.app.schemas.detection import DetectionCreate

class DetectionRepository:
  def __init__(self, db: Session):
    """
    Initialize the repository with a SQLAlchemy session.
    """
    self.db = db
    
  def save_detections(self, detections: List[DetectionCreate]) -> List[Detections]:
    """
    Save multiple detection records to the database.

    Args:
        detections: A list of validated DetectionCreate schema objects.

    Returns:
        List of newly created Detections with populated ID and timestamps.
    """
    db_detections = [Detections(**d.model_dump()) for d in detections]
    self.db.add_all(db_detections)
    self.db.commit()
    for det in db_detections:
      self.db.refresh(det)
    return db_detections
  
  def get_detection(self, detection_id: int) -> Optional[Detections]:
    """
    Retrieve a single detection by its ID.

    Args:
        detection_id: Primary key of the detection to fetch.

    Returns:
        The Detection object if found, otherwise None.
    """
    return self.db.query(Detections).filter(Detections.id == detection_id).first()
  
  def get_detections(
    skip: int = 0,
    limit: int = 100,
    species: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    sort_order: Literal["asc", "desc"] = "desc",
  ) -> List[Detections]:
    """
    Retrieve multiple detections with optional filters and sorting.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        species: Case-insensitive partial match filter for species name.
        start_date: Filter for detections after this datetime.
        end_date: Filter for detections before this datetime.
        sort_by: Column to sort by ('detection_time' or 'confidence').
        sort_order: Sorting direction ('asc' or 'desc').

    Returns:
        A list of matching Detections.
    """
    query = self.db.query(Detections)
    
    if species:
        query = query.filter(Detections.species.ilike(f"%{species}%"))
    if start_date and end_date:
        query = query.filter(Detections.detection_time.between(start_date, end_date))
    elif start_date:
        query = query.filter(Detections.detection_time >= start_date)
    elif end_date:
        query = query.filter(Detections.detection_time <= end_date)
    if sort_by and hasattr(Detections, sort_by):
        sort_column = getattr(Detections, sort_by)
        order_func = sort_column.asc if sort_order == "asc" else sort_column.desc
        query = query.order_by(order_func())

    return query.offset(skip).limit(limit).all()
  
  def delete_detection(self, detection_id: int) -> bool:
    """
    Delete a detection by its ID.

    Args:
        detection_id: Primary key of the detection to delete.

    Returns:
        True if the detection was deleted, False if not found.
    """
    detection = self.db.query(Detections).filter(Detections.id == detection_id).first()
    if detection is None:
      return False
    self.db.delete(detection)
    self.db.commit()
    return True