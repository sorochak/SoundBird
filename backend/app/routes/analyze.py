import logging
import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from backend.services.audio_analyzer import analyze_audio_file
from backend.app.utils.file_utils import get_recording_datetime, validate_upload
from backend.app.repositories.recording import RecordingRepository
from backend.app.models.recording import RecordingStatus
from database.config import get_db

router = APIRouter(tags=["analyze"])
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def analyze_audio(
    request: Request,
    file: UploadFile = File(...),
    lat: float = Form(...),
    lon: float = Form(...),
    db: Session = Depends(get_db)
):
    # Get shared BirdNET analyzer instance from app state
    analyzer = request.app.state.analyzer
    filename = validate_upload(file)
    recording_repo = RecordingRepository(db)
    detections = []
    wav_files = []
    recording_ids = []
    
    if filename.endswith(".zip"):
        with TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / filename
            with open(zip_path, "wb") as out:
                out.write(await file.read())

            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmpdir)
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="Invalid ZIP file")

            wav_files = [
                f for f in Path(tmpdir).rglob("*.[wW][aA][vV]")
                if not f.name.startswith(("._", "."))
            ]

            logger.info(f"Found {len(wav_files)} wav files in ZIP archive")

            for wav_file in wav_files:
                recording = None
                recording_id = None

                try:
                    recording_datetime = get_recording_datetime(wav_file.name)
                    recording = recording_repo.create(wav_file.name, lat, lon, recording_datetime)
                    recording_id = recording.id

                    recording_repo.update_status(recording_id, RecordingStatus.PROCESSING)

                    results = analyze_audio_file(wav_file, analyzer, recording_id, db)
                    detections.extend(results)

                    recording_repo.update_status(recording_id, RecordingStatus.COMPLETED)
                    recording_ids.append(recording_id)

                except Exception as e:
                    logger.exception(f"Failed to process {wav_file.name}")
                    if recording_id is not None:
                        recording_repo.update_status(recording_id, RecordingStatus.FAILED, error_message=str(e))

    elif filename.endswith(".wav"):
        with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp.flush()
            tmp_path = Path(tmp.name)
            
        recording = None

        try:
            recording_datetime = get_recording_datetime(tmp_path.name)
            recording = recording_repo.create(tmp_path.name, lat, lon, recording_datetime)
            recording_repo.update_status(recording.id, RecordingStatus.PROCESSING)

            results = analyze_audio_file(tmp_path, analyzer, recording.id, db)
            detections.extend(results)

            recording_repo.update_status(recording.id, RecordingStatus.COMPLETED)
            recording_ids.append(recording.id)

        except Exception as e:
            logger.exception(f"Failed to process {tmp_path.name}")
            if recording is not None:
                recording_repo.update_status(recording.id, RecordingStatus.FAILED, error_message=str(e))
        finally:
            tmp_path.unlink(missing_ok=True)

    else:
        raise HTTPException(status_code=400, detail="Only .WAV and .ZIP files are supported")

    return {
        "recording_ids": recording_ids,
        "status": "completed",
        "detections": detections,
    }