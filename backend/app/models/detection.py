# backend/app/models/detection.py

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database.config import Base


class Detections(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recording_id: Mapped[int] = mapped_column(ForeignKey("recordings.id"), nullable=False)

    detection_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    species: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scientific_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    start_sec: Mapped[float] = mapped_column(Float, nullable=False)
    end_sec: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Optional fields — currently nullable
    sonogram_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    snippet_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Many-to-one relationship: each detection is linked to one recording
    # Allows access to the parent Recording object via detection.recording
    recording = relationship(
        "Recording",                # Related model (the parent)
        back_populates="detections" # Must match field in Recording
    )

    def __repr__(self) -> str:
        return (
            f"<Detections id={self.id}, "
            f"recording_id={self.recording_id}, "
            f"detection_time={self.detection_time}, "
            f"species='{self.species}', "
            f"scientific_name='{self.scientific_name}', "
            f"confidence={self.confidence}, "
            f"start_sec={self.start_sec}, "
            f"end_sec={self.end_sec}, "
            f"created_at={self.created_at}, "
            f"sonogram_path='{self.sonogram_path}', "
            f"snippet_path='{self.snippet_path}'>"
        )