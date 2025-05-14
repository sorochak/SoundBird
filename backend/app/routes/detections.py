from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from app.models import detection as detection_model
from app.schemas import detection as detection_schema
from ..database import get_db

router = APIRouter()


@router.get("/detections", response_model=List[schemas.Detection])
def get_detections(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    species: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    # user_id: Optional[int] = None,
    sort_by: Optional[str] = Query(None, enum=["detection_time", "confidence"]),
    sort_order: Optional[str] = Query("desc", enum=["asc", "desc"]),
):
    """
    Retrieve a list of detections with optional filters and sorting.

    - species: partial match, case-insensitive
    - start_date / end_date: filter by detection_time
    - user_id: filter by user
    - sort_by: 'detection_time' or 'confidence'
    - sort_order: 'asc' or 'desc'
    """
    query = db.query(detection_model.Detections)

    if species:
        query = query.filter(models.Detections.species.ilike(f"%{species}%"))

    if user_id:
        query = query.filter(models.Detections.user_id == user_id)

    if start_date and end_date:
        query = query.filter(
            models.Detections.detection_time.between(start_date, end_date)
        )
    elif start_date:
        query = query.filter(models.Detections.detection_time >= start_date)
    elif end_date:
        query = query.filter(models.Detections.detection_time <= end_date)

    if sort_by:
        sort_column = getattr(models.Detections, sort_by, None)
        if sort_column is not None:
            if sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

    return query.offset(skip).limit(limit).all()


@router.post("/detections", response_model=List[detection_schema.Detection])
def create_detections(
    detections: List[detection_schema.DetectionCreate], db: Session = Depends(get_db)
):
    """
    Create one or more detection records in the database.

    Accepts a list of validated DetectionCreate objects and inserts them.
    Returns the inserted detections with their generated ID and created_at fields.
    """
    db_detections = [detection_model.Detections(**d.dict()) for d in detections]
    db.add_all(db_detections)
    db.commit()
    for det in db_detections:
        db.refresh(det)
    return db_detections
