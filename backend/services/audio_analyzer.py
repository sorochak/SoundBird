# audio_analyzer.py
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import os
import json
import csv
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
from tqdm import tqdm
import re
import logging

logger = logging.getLogger(__name__)

def calculate_detected_at(filename: str, start_sec: float) -> str:
    """
    Calculate the detected_at timestamp based on the filename and detection start time.

    Args:
        filename (str): WAV file name in the format 'YYYYMMDD_HHMMSS.WAV'
        start_sec (float): Seconds from start of file when detection occurs

    Returns:
        str: ISO 8601 formatted timestamp of the detection
    """
    
    match = re.match(r"(\d{8})_(\d{6})\.WAV", filename)
    if not match:
        raise ValueError(f"Invalid filename format: {filename}")

    date_str, time_str = match.groups()
    start_dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
    detected_dt = start_dt + timedelta(seconds=start_sec)
    return detected_dt.replace(microsecond=0).isoformat()


def analyze_audio_file(
    file_path: Path,
    analyzer: Analyzer,
    lat: float,
    lon: float
) -> List[Dict[str, Any]]:
    """
    Analyze a single .WAV file using BirdNETlib and return a list of detection results.

    Args:
        file_path (Path): Path to the .WAV audio file.
        analyzer (Analyzer): BirdNETlib Analyzer instance.
        lat (float): Latitude of the recording location.
        lon (float): Longitude of the recording location.

    Returns:
        List[Dict[str, Any]]: Parsed detections for the audio file.
    """
    # Extract recording date from filename (e.g., "20250425_073300.WAV")
    filename = file_path.name
    date_part = filename.split("_")[0]
    recording_date = datetime.strptime(date_part, "%Y%m%d")

    recording = Recording(
        analyzer,
        str(file_path),
        lat=lat,
        lon=lon,
        date=recording_date,
        min_conf=0.5,
    )
    
    recording.analyze()
    
    results = []
    for det in recording.detections:
        try:
            start_sec = det.get("start_time", None)
            result = {
                "file": file_path.name,
                "start_sec": start_sec,
                "end_sec": det.get("end_time", None),
                "species": det.get("common_name", "Unknown"),
                "scientific_name": det.get("scientific_name", "Unknown"),
                "label": det.get("label", ""),
                "confidence": det.get("confidence", 0.0),
                "detected_at": calculate_detected_at(file_path.name, start_sec)
                if start_sec is not None else None,
            }
            results.append(result)
        except Exception as e:
            logger.exception(f"Error saving detection for {file_path.name}")
    return results

def analyze_audio_directory(
    directory_path: Path,
    analyzer: Analyzer,
    lat: float,
    lon: float,
    output_dir="./outputs",
    output_name="predictions",
):
    """
    Analyze all WAV files in the specified directory using BirdNETlib and save the predictions.

    Args:
        directory_path (str): Path to the directory containing .wav files.
        lat (float): Latitude of the recording location.
        lon (float): Longitude of the recording location.
        output_dir (str): Directory to save prediction outputs.
        output_name (str): Base name for output files (without extension).
    """

    # Prepare output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Collect all .wav and .WAV files
    wav_files = list(Path(directory_path).glob("*.wav")) + list(
        Path(directory_path).glob("*.WAV")
    )

    all_results = []

    logger.info(f"Found {len(wav_files)} audio files in '{directory_path}'")
    logger.info(f"Using lat={lat}, lon={lon}")
    logger.info(f"Output will be saved to '{output_dir}'\n")

    start_total = time.time()

    for idx, wav_file in enumerate(tqdm(wav_files, desc="Analyzing audio files", unit="file"), 1):
        logger.info(f"[{idx}/{len(wav_files)}] Analyzing '{wav_file.name}'...")
        try:
            detections = analyze_audio_file(wav_file, analyzer, lat, lon)
            logger.info(f"Detections for {wav_file.name}: {len(detections)}")
            if detections:
                logger.debug("Sample detection:", detections[0])
            all_results.extend(detections)
        except Exception as e:
            logger.exception(f"Error analyzing '{wav_file.name}': {e}\n")

    # Save all results
    json_path = Path(output_dir) / f"{output_name}.json"
    with open(json_path, "w") as f:
        json.dump(all_results, f, indent=2)

    csv_path = Path(output_dir) / f"{output_name}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file",
                "start_sec",
                "end_sec",
                "species",
                "scientific_name",
                "label",
                "confidence",
                "detected_at",
            ],
        )
        writer.writeheader()
        writer.writerows(all_results)

    total_time = time.time() - start_total
    logger.info(f"[INFO] Analysis complete. {len(all_results)} predictions saved.")
    logger.info(f" - JSON: {json_path}")
    logger.info(f" - CSV:  {csv_path}")
    logger.info(f"[INFO] Total time: {total_time:.2f}s")
