import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import ValidationError
from backend.app.models.detection import Base, Detection
from backend.app.repositories.detection import DetectionRepository
from backend.app.schemas.detection import DetectionCreate
from backend.app.models.recording import Recording
from datetime import datetime, UTC, timezone
from typing import List, cast

# Create in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_save_detections_creates_entry(db_session):
    repo = DetectionRepository(db_session)
    det = DetectionCreate(
        recording_id=1,
        detection_time=datetime.now(UTC),
        start_sec=0.0,
        end_sec=1.0,
        species="Test Bird",
        scientific_name="Testus birdii",
        confidence=0.9,
    )
    saved = repo.save_detections([det])
    
    assert len(saved) == 1
    assert saved[0].species == "Test Bird"
    
def test_save_detections_invalid_input_raises_error(db_session):
    repo = DetectionRepository(db_session)

    # Attempt to create a DetectionCreate with missing required field 'species'
    with pytest.raises(ValidationError) as exc_info:
        det = DetectionCreate(
            recording_id=1,
            detection_time=datetime.now(UTC),
            start_sec=0.0,
            end_sec=1.0,
            species=None,  # Invalid
            scientific_name="Oopsius birdii",
            confidence=0.5,
        )
        repo.save_detections([det])

    assert "species" in str(exc_info.value)
    
def test_get_detection_returns_correct_entry(db_session):
    
    repo = DetectionRepository(db_session)
    
    det = DetectionCreate(
        recording_id=1,
        detection_time=datetime.now(UTC),
        start_sec=0.0,
        end_sec=1.0,
        species="Test Bird",
        scientific_name="Testus birdii",
        confidence=0.9,
    )
    
    saved: List[Detection] = repo.save_detections([det])

    assert saved, "No detections were saved"
    assert saved[0] is not None, "First saved detection is None"

    first_saved: Detection = saved[0]

    fetched: Detection = repo.get_detection(first_saved.id)

    assert fetched is not None, "Fetched detection is None"
    assert fetched.id == first_saved.id
    assert fetched.species == "Test Bird"
    
def test_get_detection_returns_none_for_invalid_id(db_session):
    repo = DetectionRepository(db_session)
    result = repo.get_detection(9999)
    assert result is None
    
def test_get_detections_with_species_filter(db_session):
    # Create a matching Recording row
    recording = Recording(
        id=1,
        file_name="test.wav",
        lat=48.5,
        lon=-123.4,
        recording_datetime=datetime.now(timezone.utc),
        status="COMPLETED"
    )
    db_session.add(recording)
    db_session.commit()

    # Now add the detection with matching recording_id
    repo = DetectionRepository(db_session)
    det = DetectionCreate(
        recording_id=1,
        detection_time=datetime.now(timezone.utc),
        start_sec=0.0,
        end_sec=1.0,
        species="Blue Jay",
        scientific_name="Cyanocitta cristata",
        confidence=0.8,
    )
    repo.save_detections([det])
    results = repo.get_detections(species="blue")

    assert len(results) == 1
    assert results[0].species == "Blue Jay"
    
def test_delete_detection_success(db_session):
    repo = DetectionRepository(db_session)
    det = DetectionCreate(
        recording_id=1,
        detection_time=datetime.now(UTC),
        start_sec=0.0,
        end_sec=1.0,
        species="Red Bird",
        scientific_name="Cardinalis cardinalis",
        confidence=0.7,
    )
    saved = repo.save_detections([det])
    success = repo.delete_detection(saved[0].id)
    assert success is True

def test_delete_detection_not_found_returns_false(db_session):
    repo = DetectionRepository(db_session)
    assert repo.delete_detection(9999) is False