# audio_analyzer.py
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import os
import json
import csv
import time
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm
import re


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
    return detected_dt.isoformat()

def analyze_audio_directory(
    directory_path,
    lat=48.52,
    lon=-123.40,
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
    # Initialize BirdNET-Analyzer model
    analyzer = Analyzer()

    # Prepare output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Collect all .wav and .WAV files
    wav_files = list(Path(directory_path).glob("*.wav")) + list(
        Path(directory_path).glob("*.WAV")
    )

    all_results = []

    print(f"[INFO] Found {len(wav_files)} audio files in '{directory_path}'")
    print(f"[INFO] Using lat={lat}, lon={lon}")
    print(f"[INFO] Output will be saved to '{output_dir}'\n")

    start_total = time.time()

    for idx, wav_file in enumerate(
        tqdm(wav_files, desc="Analyzing audio files", unit="file"), 1
    ):
        start_time = time.time()
        print(f"[{idx}/{len(wav_files)}] Analyzing '{wav_file.name}'...")

        try:
            # Extract recording date from filename (e.g., "20250425_073300.WAV")
            filename = wav_file.name
            date_part = filename.split("_")[0]
            recording_date = datetime.strptime(date_part, "%Y%m%d")

            # Create Recording object
            recording = Recording(
                analyzer,
                str(wav_file),
                lat=lat,
                lon=lon,
                date=recording_date,
                min_conf=0.5,  # Default confidence threshold
            )

            # Analyze the recording
            recording.analyze()
            print(f"Detections for {filename}: {len(recording.detections)}")

            # Show the structure of the first detection for debugging
            if recording.detections:
                print("Sample detection:", recording.detections[0])

            # Save detections
            for det in recording.detections:
                try:
                    start_sec = det.get("start_time", None)
                    result = {
                        "file": wav_file.name,
                        "start_sec": start_sec,
                        "end_sec": det.get("end_time", None),
                        "species": det.get("common_name", "Unknown"),
                        "scientific_name": det.get("scientific_name", "Unknown"),
                        "label": det.get("label", ""),
                        "confidence": det.get("confidence", 0.0),
                        "detected_at": calculate_detected_at(wav_file.name, start_sec)
                        if start_sec is not None else None,
                    }
                    all_results.append(result)
                except Exception as e:
                    print(f"Error saving detection for {wav_file.name}: {e}")
        except Exception as e:
            print(f"Error analyzing '{wav_file.name}': {e}\n")

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
    print(f"[INFO] Analysis complete. {len(all_results)} predictions saved.")
    print(f" - JSON: {json_path}")
    print(f" - CSV:  {csv_path}")
    print(f"[INFO] Total time: {total_time:.2f}s")
