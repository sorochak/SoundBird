# backend/app/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DetectionCreate(BaseModel):
    """
    Schema for creating a new detection.
    """

    file_name: str
    recording_datetime: datetime
    detection_time: datetime
    species: str
    scientific_name: str
    confidence: float
    start_sec: float
    end_sec: float
    lat: float
    lon: float
    image_path: Optional[str] = None
    sonogram_path: Optional[str] = None
    snippet_path: Optional[str] = None
    # user_id: Optional[int] = None  # Uncomment when user authentication is implemented


class Detection(DetectionCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
