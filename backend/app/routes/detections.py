from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from datetime import datetime
from backend.app.schemas import detection as detection_schema
from backend.app.crud import detection as crud_detection
from database.config import get_db


router = APIRouter()


@router.get("/detections/{detection_id}", response_model=detection_schema.Detection)
def get_detection(detection_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single detection by its unique ID.

    - **detection_id**: Required. The primary key of the detection record.

    Returns:
    - 200: Detection found and returned.
    - 404: Detection not found.
    """
    detection = crud_detection.get_detection(db, detection_id)
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.get("/detections", response_model=List[detection_schema.Detection])
def get_detections(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    species: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: Optional[Literal["detection_time", "confidence"]] = Query(None),
    sort_order: Literal["asc", "desc"] = Query("desc"),
):
    """
    Retrieve a list of detections with optional filters and sorting.

    - species: partial match, case-insensitive
    - start_date / end_date: filter by detection_time
    - sort_by: 'detection_time' or 'confidence'
    - sort_order: 'asc' or 'desc'
    """
    return crud_detection.get_detections(
        db=db,
        skip=skip,
        limit=limit,
        species=species,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post(
    "/detections", response_model=List[detection_schema.Detection], status_code=201
)
def create_detections(
    detections: List[detection_schema.DetectionCreate], db: Session = Depends(get_db)
):
    """
    Create one or more detection records in the database.

    Accepts a list of validated DetectionCreate objects and inserts them.
    Returns the inserted detections with their generated ID and created_at fields.
    """
    return crud_detection.create_detections(db, detections)


@router.delete("/detections/{detection_id}", status_code=204)
def delete_detection(detection_id: int, db: Session = Depends(get_db)):
    """
    Delete a detection by its ID.
    Returns 204 if deleted, 404 if not found.
    """
    deleted = crud_detection.delete_detection(db, detection_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Detection not found")
    return
