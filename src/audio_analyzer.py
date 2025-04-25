from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import os
import json
import csv
import time
from pathlib import Path
from datetime import datetime
from tqdm import tqdm


def analyze_audio_directory(
    directory_path, lat=48.52, lon=-123.40, output_dir="./outputs"
):
    """
    Analyze all WAV files in the specified directory using BirdNETlib and save the predictions.

    Args:
        directory_path (str): Path to the directory containing .wav files.
        lat (float): Latitude of the recording location.
        lon (float): Longitude of the recording location.
        output_dir (str): Directory to save prediction outputs.
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
                    result = {
                        "file": wav_file.name,
                        "start_sec": det.get("start_time", None),
                        "end_sec": det.get("end_time", None),
                        "species": det.get("common_name", "Unknown"),
                        "scientific_name": det.get("scientific_name", "Unknown"),
                        "label": det.get("label", ""),
                        "confidence": det.get("confidence", 0.0),
                    }
                    all_results.append(result)
                except Exception as e:
                    print(f"Error saving detection for {wav_file.name}: {e}")

            elapsed = time.time() - start_time
            print(f"Done in {elapsed:.2f}s\n")

        except Exception as e:
            print(f"Error analyzing '{wav_file.name}': {e}\n")

    # Save all results
    json_path = Path(output_dir) / "predictions.json"
    with open(json_path, "w") as f:
        json.dump(all_results, f, indent=2)

    csv_path = Path(output_dir) / "predictions.csv"
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
            ],
        )
        writer.writeheader()
        writer.writerows(all_results)

    total_time = time.time() - start_total
    print(f"[INFO] Analysis complete. {len(all_results)} predictions saved.")
    print(f" - JSON: {json_path}")
    print(f" - CSV:  {csv_path}")
    print(f"[INFO] Total time: {total_time:.2f}s")
