from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


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

    model_config = {"from_attributes": True}
