from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Float, Text, Enum as SAEnum
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
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(nullable=True)

    def __repr__(self):
        return (
            f"<Recording id={self.id}, "
            f"file_name='{self.file_name}', "
            f"status='{self.status}', "
            f"lat={self.lat}, "
            f"lon={self.lon}, "
            f"created_at={self.created_at}, "
            f"completed_at={self.completed_at}, "
            f"error_message='{self.error_message}'>"
        )
