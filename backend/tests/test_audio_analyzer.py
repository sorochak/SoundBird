# backend/tests/test_audio_analyzer.py

import pytest
from backend.services.audio_analyzer import calculate_detected_at

def test_calculate_detected_at_valid():
    filename = "20231001_123456.WAV"
    start_sec = 10.0
    expected_result = "2023-10-01T12:35:06" 
    result = calculate_detected_at(filename, start_sec)
    assert result == expected_result

def test_calculate_detected_at_invalid_filename():
    with pytest.raises(ValueError, match="Invalid filename format"):
        calculate_detected_at("invalid_filename.wav", 10.0)

def test_calculate_detected_at_zero_seconds():
    filename = "20231001_123456.WAV"
    start_sec = 0.0
    expected_result = "2023-10-01T12:34:56"  # Exact time from filename
    result = calculate_detected_at(filename, start_sec)
    assert result == expected_result
