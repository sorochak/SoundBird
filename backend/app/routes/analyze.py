from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path
import zipfile
from typing import List
import logging
from backend.services.audio_analyzer import analyze_audio_file

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def analyze_audio(
    request: Request,
    file: UploadFile = File(...),
    lat: float = Form(...),
    lon: float = Form(...),
):
    analyzer = request.app.state.analyzer
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

    filename = file.filename.lower()

    if filename.endswith(".wav"):
        with NamedTemporaryFile(delete=True, suffix=".wav") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp.flush()
            tmp_path = Path(tmp.name)
            original_filename = file.filename
            tmp_path_with_name = tmp_path.with_name(original_filename)
            tmp_path.rename(tmp_path_with_name)
            logger.info(f"Analyzing uploaded file: {original_filename}")
            detections = analyze_audio_file(tmp_path_with_name, analyzer, lat, lon)
            return {"detections": detections}

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

            all_detections = []
            
            wav_files = list(Path(tmpdir).rglob("*.[wW][aA][vV]"))
            logger.info(f"Found {len(wav_files)} wav files in ZIP archive")

            for wav_file in wav_files:
                try:
                    results = analyze_audio_file(wav_file, analyzer, lat, lon)
                    all_detections.extend(results)
                except Exception as e:
                    logger.warning(f"Skipping {wav_file.name}: {e}")

            return {"detections": all_detections}

    else:
        raise HTTPException(status_code=400, detail="Only .WAV and .ZIP files are supported")
