# FastAPI utilities for routing and handling file uploads
# backend/app/routes/analyze.py
from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path
import zipfile
from typing import List
import logging

# Core services for audio analysis and database operations
from backend.services.audio_analyzer import analyze_audio_file
from backend.services.recordings import create_recording, update_recording_status
from database.config import SessionLocal
from backend.app.models.recording import RecordingStatus

# Create a router for the analyze endpoint
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def analyze_audio(
    request: Request,
    file: UploadFile = File(...), # Uploaded .wav or .zip file
    lat: float = Form(...),       # Latitude from form input
    lon: float = Form(...),       # Longitude from form input
):
    # Get shared BirdNET analyzer instance from app state
    analyzer = request.app.state.analyzer
    
    # Validate that the uploaded file has a filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

    filename = file.filename.lower()
    
    # Step 1: Create a new row in the recordings table with status=PENDING
    db = SessionLocal()
    try:
        recording = create_recording(db, file_name=filename, lat=lat, lon=lon)
        recording_id = recording.id
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

    try:
        # Step 2: Update to PROCESSING
        db = SessionLocal()
        update_recording_status(db, recording_id, RecordingStatus.PROCESSING)
        db.close()

        if filename.endswith(".wav"):
            with NamedTemporaryFile(delete=True, suffix=".wav") as tmp:
                contents = await file.read()
                tmp.write(contents)
                tmp.flush()
                tmp_path = Path(tmp.name)
                tmp_path_with_name = tmp_path.with_name(file.filename)
                tmp_path.rename(tmp_path_with_name)
                logger.info(f"Analyzing uploaded file: {file.filename}")
                detections = analyze_audio_file(tmp_path_with_name, analyzer, lat, lon)

        elif filename.endswith(".zip"):
            with TemporaryDirectory() as tmpdir:
                tmp_zip_path = Path(tmpdir) / filename
                with open(tmp_zip_path, "wb") as out:
                    out.write(await file.read())

                try:
                    with zipfile.ZipFile(tmp_zip_path, "r") as zip_ref:
                        zip_ref.extractall(tmpdir)
                except zipfile.BadZipFile:
                    raise HTTPException(status_code=400, detail="Invalid ZIP file")

                detections = []
                wav_files = list(Path(tmpdir).rglob("*.[wW][aA][vV]"))
                logger.info(f"Found {len(wav_files)} wav files in ZIP archive")

                for wav_file in wav_files:
                    try:
                        results = analyze_audio_file(wav_file, analyzer, lat, lon)
                        detections.extend(results)
                    except Exception as e:
                        logger.warning(f"Skipping {wav_file.name}: {e}")

        else:
            raise HTTPException(status_code=400, detail="Only .WAV and .ZIP files are supported")

        # Step 3: Update to COMPLETED
        db = SessionLocal()
        update_recording_status(db, recording_id, RecordingStatus.COMPLETED)
        db.close()
        return {"recording_id": recording_id, "status": "completed", "detections": detections}

    except Exception as e:
        logger.exception("Error during analysis")
        db = SessionLocal()
        update_recording_status(db, recording_id, RecordingStatus.FAILED, error_message=str(e))
        db.close()
        raise HTTPException(status_code=500, detail="Internal error during analysis")