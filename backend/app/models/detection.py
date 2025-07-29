# backend/app/models/detection.py

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func

from database.config import Base  # You can keep this if Base = declarative_base() in config.py


class Detections(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    recording_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    detection_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    species: Mapped[str] = mapped_column(String, nullable=False)
    scientific_name: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    start_sec: Mapped[float] = mapped_column(Float, nullable=False)
    end_sec: Mapped[float] = mapped_column(Float, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Optional fields — currently nullable
    image_path: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    sonogram_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    snippet_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    def __repr__(self) -> str:
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
            f"snippet_path='{self.snippet_path}'>"
        )