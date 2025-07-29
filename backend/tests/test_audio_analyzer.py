# backend/tests/test_audio_analyzer.py

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any
from backend.services.audio_analyzer import (
    calculate_detection_time,
    analyze_audio_file,
)
from birdnetlib.analyzer import Analyzer

def test_calculate_detection_time_valid():
    filename = "20231001_123456.WAV"
    start_sec = 10.0
    expected_result = datetime(2023, 10, 1, 12, 35, 6)
    result = calculate_detection_time(filename, start_sec)
    assert result == expected_result

def test_calculate_detection_time_invalid_filename():
    with pytest.raises(ValueError, match="Invalid filename format"):
        calculate_detection_time("invalid_filename.wav", 10.0)

def test_calculate_detection_time_zero_seconds():
    filename = "20231001_123456.WAV"
    start_sec = 0.0
    expected_result = datetime(2023, 10, 1, 12, 34, 56)
    result = calculate_detection_time(filename, start_sec)
    assert result == expected_result

@patch("backend.services.audio_analyzer.Recording")
def test_analyze_audio_file_mocked(mock_recording_class):
    mock_recording = MagicMock()
    mock_recording.detections = [
        {
            "start_time": 12.3,
            "end_time": 14.5,
            "common_name": "Raven",
            "scientific_name": "Corvus corax",
            "label": "RAVN",
            "confidence": 0.85,
        }
    ]
    mock_recording_class.return_value = mock_recording

    analyzer = MagicMock()
    file_path = Path("tests/data/20231001_123456.WAV")
    lat, lon = 48.52, -123.40

    results = analyze_audio_file(file_path, analyzer, lat, lon)

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["species"] == "Raven"
    assert results[0]["confidence"] == 0.85
    assert results[0]["detection_time"] == "2023-10-01T12:35:08.300000"
