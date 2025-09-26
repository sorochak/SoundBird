# audio_analyzer.py
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from birdnetlib import Recording as BirdNETRecording
from birdnetlib.analyzer import Analyzer

from sqlalchemy.orm import Session

from backend.app.repositories.detection import DetectionRepository
from backend.app.repositories.recording import RecordingRepository
from backend.app.schemas.detection import DetectionCreate
from backend.app.schemas.detection import DetectionResponse
from backend.app.utils.file_utils import calculate_detection_time

logger = logging.getLogger(__name__)

def analyze_audio_file(
    file_path: Path,
    analyzer: Analyzer,
    recording_id: int,
    db: Session
) -> List[DetectionResponse]:
    """
    Analyze a single .WAV file using BirdNETlib and store detections linked to the given recording ID.

    Args:
        file_path (Path): Path to the .WAV audio file.
        analyzer (Analyzer): BirdNETlib Analyzer instance.
        recording_id (int): ID of the associated recording row in the DB.
        db (Session): SQLAlchemy DB session.

    Returns:
        List[DetectionResponse]: The detection records created.
    """
    try:
        # Fetch recording metadata for BirdNET
        recording_metadata = RecordingRepository(db).get(recording_id)
        if not recording_metadata:
            raise ValueError(f"Recording with ID {recording_id} not found")
        
        birdnet_recording = BirdNETRecording(
            analyzer=analyzer,
            path=str(file_path),
            lat=recording_metadata.lat,
            lon=recording_metadata.lon,
            date=recording_metadata.recording_datetime.date(),
            min_conf=0.5,
        )
        
        birdnet_recording.analyze()
        
    except Exception as e:
        logger.exception(f"Failed to initialize or run BirdNET on {file_path.name}")
        raise
    
    # Parse detections
    results_to_save: List[DetectionCreate] = []
    results_to_return: List[DetectionResponse] = []
    
    for det in birdnet_recording.detections:
        try:
            # Build the DB save schema
            to_save = DetectionCreate(
                recording_id=recording_id,
                detection_time=calculate_detection_time(file_path.name, det["start_time"]),
                start_sec=det["start_time"],
                end_sec=det["end_time"],
                species=det["common_name"],
                scientific_name=det["scientific_name"],
                confidence=det["confidence"],
            )
            results_to_save.append(to_save)
            
            # Build the enriched response schema
            to_return = DetectionResponse(
                file_name=recording_metadata.file_name,
                recording_datetime=recording_metadata.recording_datetime,
                lat=recording_metadata.lat,
                lon=recording_metadata.lon,
                detection_time=to_save.detection_time,
                start_sec=to_save.start_sec,
                end_sec=to_save.end_sec,
                species=to_save.species,
                scientific_name=to_save.scientific_name,
                confidence=to_save.confidence,
            )
            results_to_return.append(to_return)
        except Exception as e:
            logger.exception(f"Error parsing detection in {file_path.name}")
            
    # Save all parsed detections
        
    if results_to_save:
        logger.info(f"Parsed {len(results_to_save)} detections from {file_path.name}")
        try:
            DetectionRepository(db).save_detections(results_to_save)
            logger.info(f"Saved {len(results_to_save)} detections for recording ID {recording_id}")
        except Exception as e:
            logger.exception(f"Failed to save detections to DB for {file_path.name}")
    else:
        logger.warning(f"No detections found in file {file_path.name}")
                
    return results_to_return