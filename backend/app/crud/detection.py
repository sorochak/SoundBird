from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from datetime import datetime
from backend.app.models.detection import Detections
from backend.app.schemas.detection import DetectionCreate

def get_detection(db: Session, detection_id: int) -> Optional[Detections]:
    """
    Retrieve a single detection by its ID.

    Args:
        db (Session): SQLAlchemy database session.
        detection_id (int): The ID of the detection to retrieve.

    Returns:
        Optional[Detections]: The detection object if found, else None.
    """
    return db.query(Detections).filter(Detections.id == detection_id).first()

def create_detections(
    db: Session,  # SQLAlchemy DB session passed from FastAPI's dependency injection
    detections: List[
        DetectionCreate
    ],  # List of input objects from the client (validated)
) -> List[Detections]:  # Returns the created DB model instances with ID and timestamps
    """
    Create multiple detections in the database.

    Args:
        db (Session): SQLAlchemy database session.
        detections (List[DetectionCreate]): Validated detection data from client.

    Returns:
        List[Detections]: List of newly created detection records.
    """

    # Convert each DetectionCreate Pydantic object into a SQLAlchemy Detections model instance
    # d.model_dump() converts the Pydantic model into a plain dictionary of field values.
    # This dictionary is unpacked into keyword arguments for the Detections SQLAlchemy model.
    db_detections = [Detections(**d.model_dump()) for d in detections]

    # Add all detection objects to the session
    db.add_all(db_detections)

    # commit the transaction to save the detections in the database
    db.commit()

    # refresh each object ot load generated fields like ID and created_at from the database
    for det in db_detections:
        db.refresh(det)

    # Return the fully saved detection objects so they can be returned in the API response
    return db_detections


def get_detections(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    species: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    sort_order: Literal["asc", "desc"] = "desc",
) -> List[Detections]:
    """
    Retrieve detections with optional filters and pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip (for pagination).
        limit (int): Maximum number of records to return.
        species (Optional[str]): Filter by species name.
        start_date (Optional[datetime]): Filter detections after this date.
        end_date (Optional[datetime]): Filter detections before this date.
        sort_by (Optional[str]): Field to sort by.
        sort_order (Optional[str]): Sort direction ('asc' or 'desc').

    Returns:
        List[Detections]: List of filtered and sorted detection records.
    """
    query = db.query(Detections)

    if species:
        query = query.filter(Detections.species.ilike(f"%{species}%"))

    if start_date and end_date:
        query = query.filter(Detections.detection_time.between(start_date, end_date))
    elif start_date:
        query = query.filter(Detections.detection_time >= start_date)
    elif end_date:
        query = query.filter(Detections.detection_time <= end_date)

    if sort_by is not None:
        if hasattr(Detections, sort_by):
            sort_column = getattr(Detections, sort_by)
            if sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

    return query.offset(skip).limit(limit).all()


def delete_detection(db: Session, detection_id: int) -> bool:
    """
    Delete a detection by its ID.

    Args:
        db (Session): SQLAlchemy database session.
        detection_id (int): The ID of the detection to delete.

    Returns:
        bool: True if deleted successfully, False if not found.
    """
    detection = db.query(Detections).filter(Detections.id == detection_id).first()
    if detection is None:
        return False
    db.delete(detection)
    db.commit()
    return True
