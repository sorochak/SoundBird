# backend/app/models/detection.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base


class Detections(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    recording_datetime = Column(DateTime(timezone=True), nullable=False)
    detection_time = Column(DateTime(timezone=True), nullable=False)
    species = Column(String, nullable=False)
    scientific_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    start_sec = Column(Float, nullable=False)
    end_sec = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Optional fields for now - UPDATE TO nullable=False LATER WHEN FEATURES ARE WORKING
    image_path = Column(String, index=True)
    sonogram_path = Column(String)
    snippet_path = Column(String)
    # user_id = Column(Integer, ForeignKey("users.id"))

    def __repr__(self):
        return (
            f"<Detections id={self.id}, "
            f"file_name='{self.file_name}', "
            f"recording_datetime={self.recording_datetime}, "
            f"detection_time={self.detection_time}, "
            f"species='{self.species}', "
            f"scientific_name='{self.scientific_name}', "
            f"confidence={self.confidence}, "
            f"start_sec={self.start_sec}, "
            f"end_sec={self.end_sec}, "
            f"lat={self.lat}, "
            f"lon={self.lon}, "
            f"created_at={self.created_at}, "
            f"image_path='{self.image_path}', "
            f"sonogram_path='{self.sonogram_path}', "
            f"snippet_path='{self.snippet_path}', "
            # f"user_id={self.user_id}>"
        )
