from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum
from sqlalchemy.sql import func
from database.config import Base
import enum

class RecordingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    recording_datetime = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(RecordingStatus), default=RecordingStatus.PENDING, nullable=False)
    duration_sec = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return (
            f"<Recording id={self.id}, "
            f"file_name='{self.file_name}', "
            f"recording_datetime={self.recording_datetime}, "
            f"status='{self.status}', "
            f"duration_sec={self.duration_sec}, "
            f"lat={self.lat}, "
            f"lon={self.lon}, "
            f"created_at={self.created_at}, "
            f"completed_at={self.completed_at}, "
            f"error_message='{self.error_message}'>"
        )
