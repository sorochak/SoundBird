from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Float, Text, Integer, String, Enum as SAEnum
from sqlalchemy.sql import func
from database.config import Base
from datetime import datetime
import enum

class RecordingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Recording(Base):
    __tablename__ = "recordings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[RecordingStatus] = mapped_column(SAEnum(RecordingStatus), default=RecordingStatus.PENDING, nullable=False)
    lat: Mapped[float] = mapped_column(nullable=False)
    lon: Mapped[float] = mapped_column(nullable=False)
    recording_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(nullable=True)
    
    # Relationship
    detections = relationship("Detections", back_populates="recording", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<Recording id={self.id}, "
            f"file_name='{self.file_name}', "
            f"status='{self.status}', "
            f"recording_datetime={self.recording_datetime}, "
            f"lat={self.lat}, "
            f"lon={self.lon}, "
            f"created_at={self.created_at}, "
            f"completed_at={self.completed_at}, "
            f"error_message='{self.error_message}'>"
        )
