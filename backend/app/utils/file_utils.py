import re
from datetime import datetime, timedelta
from fastapi import UploadFile, HTTPException

def validate_upload(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

    filename = file.filename.lower()

    if not filename.endswith((".wav", ".zip")):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: '{filename}'. Only .wav or .zip files are allowed."
        )

    if filename.endswith(".wav"):
        if not re.match(r"\d{8}_\d{6}\.wav", filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid .wav filename format: '{filename}'. Expected 'YYYYMMDD_HHMMSS.wav'."
            )

    return filename

def get_recording_datetime(filename:str) -> datetime:
    """
    Extract the recording date and time from the filename.

    Args:
        filename (str): WAV file name in the format 'YYYYMMDD_HHMMSS.WAV'

    Returns:
        datetime: Recording date and time as a datetime object.
    
    Raises:
        ValueError: If the filename format is invalid.
    """
    filename = filename.lower()
    match = re.match(r"(\d{8})_(\d{6})\.wav", filename)
    if not match:
        raise ValueError(f"Invalid filename format: {filename}")

    date_str, time_str = match.groups()
    return datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")

def calculate_detection_time(filename: str, start_sec: float) -> datetime:
    """
    Calculates the actual time a detection occurred, based on the file name and start seconds.

    Args:
        filename (str): The name of the file.
        start_sec (float): Seconds after the recording began.

    Returns:
        datetime: The exact timestamp of the detection.
    """
    recording_start = get_recording_datetime(filename)
    return recording_start + timedelta(seconds=start_sec)