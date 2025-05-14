from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.app.models.detection import Detections
from backend.app.schemas.detection import DetectionCreate


# Get a single detection from the database by its ID.
# Returns None if the detection is not found.
# This function is useful for retrieving a specific detection's details.
# It can be used in various scenarios, such as displaying detailed information about a detection
# in a web application or API response.
# The function takes a SQLAlchemy session and the detection ID as parameters.


def get_detection(db: Session, detection_id: int) -> Optional[Detections]:
    return db.query(Detections).filter(Detections.id == detection_id).first()


# This function creates multiple detections in the database.
# It takes a SQLAlchemy session and a list of DetectionCreate objects as parameters.
# Each detection comes in as a validated Pydantic model, (DetectionCreate).
# The function converts each DetectionCreate object into a Detections model instance,


def create_detections(
    db: Session,  # SQLAlchemy DB session passed from FastAPI's dependency injection
    detections: List[
        DetectionCreate
    ],  # List of input objects from the client (validated)
) -> List[Detections]:  # Returns the created DB model instances with ID and timestamps

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
    user_id: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc",
) -> List[Detections]:
    query = db.query(Detections)

    if species:
        query = query.filter(Detections.species.ilike(f"%{species}%"))

    if user_id:
        query = query.filter(Detections.user_id == user_id)

    if start_date and end_date:
        query = query.filter(Detections.detection_time.between(start_date, end_date))
    elif start_date:
        query = query.filter(Detections.detection_time >= start_date)
    elif end_date:
        query = query.filter(Detections.detection_time <= end_date)

    if sort_by:
        sort_column = getattr(Detections, sort_by, None)
        if sort_column is not None:
            query = query.order_by(getattr(sort_column, sort_order)())

    return query.offset(skip).limit(limit).all()


def delete_detection(db: Session, detection_id: int) -> bool:
    """
    Delete a detection by its ID.
    Returns True if the detection was deleted, False if not found.
    """
    detection = db.query(Detections).filter(Detections.id == detection_id).first()
    if detection is None:
        return False
    db.delete(detection)
    db.commit()
    return True
