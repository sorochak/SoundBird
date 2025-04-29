# services/run_audio_analysis.py

from audio_analyzer import analyze_audio_directory
from pathlib import Path

if __name__ == "__main__":
    # Define the path to the audio files directory
    recordings_root = Path("./recordings")

    # Automatically find all subdirectories inside recordings/
    day_folders = [f for f in recordings_root.iterdir() if f.is_dir()]

    # Check if the directory exists
    if not day_folders:
        print("[ERROR] No recording folders found inside './recordings/'")
        exit(1)

    print(f"[INFO] Found {len(day_folders)} day folders to analyze.")

    for day_folder in day_folders:
        print(f"\n[INFO] Analyzing folder: {day_folder}")

        output_folder = Path("./outputs") / day_folder.name

        analyze_audio_directory(
            directory_path=day_folder,
            output_dir=output_folder,
            lat=48.432785371465926,
            lon=-123.46746108465791,
        )
        print(f"[INFO] Finished analyzing folder: {day_folder}")
