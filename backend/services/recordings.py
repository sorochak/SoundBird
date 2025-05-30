from sqlalchemy.orm import Session
from app.models.recording import Recording, RecordingStatus
from datetime import datetime

def create_recording(db: Session, *, file_name: str, recording_datetime: datetime, duration_sec: float, lat: float, lon: float) -> Recording:
    new_recording = Recording(
        file_name=file_name,
        recording_datetime=recording_datetime,
        duration_sec=duration_sec,
        lat=lat,
        lon=lon,
        status=RecordingStatus.PENDING,
    )
    db.add(new_recording)
    db.commit()
    db.refresh(new_recording)
    return new_recording

def update_recording_status(db: Session, recording_id: int, status: RecordingStatus, error_message: str | None = None) -> Recording:
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        raise ValueError(f"Recording with id {recording_id} not found.")
    
    recording.status = status
    if status == RecordingStatus.COMPLETED:
        recording.completed_at = datetime.utcnow()
    elif status == RecordingStatus.FAILED:
        recording.error_message = error_message
    
    db.commit()
    db.refresh(recording)
    return recording
  
def get_all_recordings(db: Session, status: RecordingStatus | None = None) -> list[Recording]:
    query = db.query(Recording)
    if status:
        query = query.filter(Recording.status == status)
    return query.order_by(Recording.created_at.desc()).all()