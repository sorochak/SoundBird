# SoundBird

**SoundBird** is a full-stack web application for analyzing bird audio recordings, detecting species, visualizing biodiversity patterns, and sharing discoveries.

Built for researchers, conservationists, and nature enthusiasts, SoundBird enables users to upload field recordings (e.g., from devices like [AudioMoth](https://www.openacousticdevices.info/audiomoth)), automatically detect bird species using machine learning models like BirdNET, and explore the results through an interactive frontend.  
The system highlights species presence across time and location, generates AI-assisted species thumbnails, and flags endangered or at-risk species based on detections.
It transforms raw acoustic data into dynamic visualizations, species profiles, and conservation insights — making bioacoustics research more accessible, engaging, and actionable.

SoundBird is currently under active development. It will allow users to:

- Upload and analyze recordings from field devices
- Detect bird species using BirdNET
- Generate AI-assisted photorealistic species thumbnails and summaries
- Visualize biodiversity trends across time and space
- Explore trends, hotspots, and potential conservation insights

## Current Features

- **Audio Analysis with BirdNET**: Detects bird species automatically from uploaded `.wav` recordings using BirdNET.
- **Detection Persistence with PostgreSQL**: After each audio file is analyzed, all detections are saved directly to PostgreSQL. Batched inserts improve performance, and detection timestamps are parsed from filenames.
- **Dynamic Species Thumbnail Generation**: Uses generative AI to create realistic species thumbnails based on real bird traits, enriching species profiles.
- **Wikipedia Species Descriptions**: Fetches detailed descriptions to enrich detection results.
- **Automated Data Pipeline**: Processes large batches of field recordings into structured outputs, saving results as `.csv` and `.json`.
- **Scalable Web Architecture**: Designed to grow into a cloud-based platform with map-based exploration, detection timelines, habitat overlays, and more.

---

## Tech Stack and Justification

| Technology         | Purpose                     | Why It’s Used                                                         |
| ------------------ | --------------------------- | --------------------------------------------------------------------- |
| **FastAPI**        | Web framework               | Lightweight, async-ready, and ideal for API-centric applications      |
| **SQLAlchemy**     | ORM for database access     | Clean and declarative way to model data using Python classes          |
| **Alembic**        | Database migrations         | Enables version-controlled schema changes                             |
| **PostgreSQL**     | Relational database         | Reliable, scalable, and feature-rich SQL database for structured data |
| **Docker Compose** | Dev environment management  | Simplifies provisioning of PostgreSQL in local development            |
| **BirdNETlib**     | ML model for bird detection | Provides local, pre-trained species detection from `.wav` files       |
| **OpenAI API**     | Image generation            | Generates species thumbnails using natural language prompts           |
| **Pydantic**       | Data validation             | Validates and serializes request and response data in FastAPI         |
| **TQDM**           | CLI progress visualization  | Visualizes batch analysis progress during long-running scripts        |
| **python-dotenv**  | Env variable loading        | Keeps secrets and config out of source code, loaded from `.env` file  |

---

## Data Model

### Current Schema: `detections` Table

| Column               | Type     | Description                                  |
| -------------------- | -------- | -------------------------------------------- |
| `id`                 | Integer  | Primary key                                  |
| `file_name`          | String   | Name of the analyzed file                    |
| `recording_datetime` | DateTime | Start time of the recording                  |
| `detection_time`     | DateTime | Timestamp of detected call                   |
| `species`            | String   | Common species name                          |
| `scientific_name`    | String   | Scientific name of the species               |
| `confidence`         | Float    | Confidence score from the model              |
| `start_sec`          | Float    | Detection start time (relative to recording) |
| `end_sec`            | Float    | Detection end time                           |
| `lat`                | Float    | Latitude of the recording location           |
| `lon`                | Float    | Longitude of the recording location          |
| `created_at`         | DateTime | Timestamp when row was inserted              |
| `image_path`         | String   | Optional path to species thumbnail           |
| `sonogram_path`      | String   | Optional path to generated sonogram          |
| `snippet_path`       | String   | Optional path to audio snippet               |

---

### Planned Schema: Normalized with `recordings` Table

#### Table: `recordings` (new)

| Column          | Type     | Description                                      |
| --------------- | -------- | ------------------------------------------------ |
| `id`            | Integer  | Primary key                                      |
| `file_name`     | String   | Name of the uploaded audio file                  |
| `status`        | Enum     | Processing status (`pending`, `completed`, etc.) |
| `lat`           | Float    | Latitude of recording                            |
| `lon`           | Float    | Longitude of recording                           |
| `created_at`    | DateTime | Time recording was uploaded                      |
| `completed_at`  | DateTime | Time analysis finished                           |
| `error_message` | String   | Optional error message if processing failed      |

#### Table: `detections` (updated)

| Column               | Type     | Description                                  |
| -------------------- | -------- | -------------------------------------------- |
| `id`                 | Integer  | Primary key                                  |
| `recording_id`       | Integer  | Foreign key referencing `recordings.id`      |
| `recording_datetime` | DateTime | Start time of the recording                  |
| `detection_time`     | DateTime | Timestamp of detected call                   |
| `species`            | String   | Common species name                          |
| `scientific_name`    | String   | Scientific name of the species               |
| `confidence`         | Float    | Confidence score from the model              |
| `start_sec`          | Float    | Detection start time (relative to recording) |
| `end_sec`            | Float    | Detection end time                           |
| `image_path`         | String   | Optional path to species thumbnail           |
| `sonogram_path`      | String   | Optional path to generated sonogram          |
| `snippet_path`       | String   | Optional path to audio snippet               |
| `created_at`         | DateTime | Timestamp when row was inserted              |

---

## High-Level System Data Flow

1. User submits a `.wav` or `.zip` file via the `POST /analyze` route.
2. `routes/analyze.py` receives the file and passes it to `analyze_audio_file()` in `services/audio_analyzer.py`.
3. `services/audio_analyzer.py` uses BirdNET to analyze audio, enriches detections, and calls the `DetectionRepository` to persist results.
4. `repositories/detection.py` handles database access and inserts detection records via SQLAlchemy ORM.
5. `models/detection.py` defines the DB schema (tables and columns).
6. `schemas/detection.py` defines Pydantic schemas for validation and serialization.
7. User can fetch stored detections through `GET /detections` and related CRUD endpoints in `routes/detections.py`.

---

## Module Descriptions

### `main.py`

**Purpose**: Main FastAPI entry point.

**Responsibilities**:

- Instantiates the FastAPI app
- Sets up health check and middleware
- Includes route routers (`/analyze`, `/detections`)
- Optionally sets up shared app state (e.g., BirdNET Analyzer instance)

---

### `routes/detections.py`

**Purpose**: Exposes CRUD endpoints for detection records.

**Responsibilities**:

- Define RESTful endpoints: `GET /detections`, `GET /detections/{id}`, `DELETE /detections/{id}`
- Delegate business logic to `DetectionRepository`
- Serialize responses using Pydantic schemas

---

### `routes/analyze.py`

**Purpose**: Handles audio upload and analysis.

**Responsibilities**:

- Accept `.wav` or `.zip` uploads via `POST /analyze`
- Extract metadata (lat/lon)
- Call `analyze_audio_file()` in `services/audio_analyzer.py`
- Return success or error response

---

### `schemas/detection.py`

**Purpose**: Defines request and response shapes using Pydantic.

**Responsibilities**:

- `DetectionCreate`: incoming payload for new detections
- `Detection`: response model (matches DB schema + ID)
- Enables type-checking, validation, and Swagger docs

---

### `models/detection.py`

**Purpose**: SQLAlchemy model for the `detections` table.

**Responsibilities**:

- Define database schema (columns, types, constraints)
- Maps to a table in PostgreSQL
- Used by repository layer for ORM operations

---

### `repositories/detection.py`

**Purpose**: Implements database access using the Repository pattern.

**Responsibilities**:

- `save_detections()`: bulk insert detection records
- `get_detection()`, `get_detections()`, `delete_detection()`
- Keeps DB logic decoupled from route and service layers

---

### `services/audio_analyzer.py`

**Purpose**: Orchestrates audio analysis using BirdNET and handles detection parsing.

**Responsibilities**:

- Accept a `.wav` file or directory of files
- Use BirdNETlib to extract detection data
- Parse and enrich metadata (datetime, lat/lon, filename)
- Delegate persistence to `DetectionRepository`

## System Architecture Overview

SoundBird is currently under active development.  
The following system diagrams reflect the **planned system architecture** and current **audio upload flow**.

### Planned System Architecture

<p align="center">
  <img src="docs/architecture/soundbird-system-architecture-transparent.png" width="500px">
</p>

---

### Audio Upload Flow

_This diagram shows the step-by-step flow when a user uploads an audio file for species detection:_

![SoundBird Audio Upload Flow](docs/architecture/soundbird-audio-upload-flow-transparent.png)

---

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/soundbird.git
cd soundbird
```

2. **Set up your virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
```

3. **Install project dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set your environment variables:**

Create a `.env` file in the root folder:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

---

## Database Setup (PostgreSQL + Alembic)

SoundBird uses PostgreSQL as its database and Alembic for schema migrations.

➡️ See [`database/README.md`](database/README.md) for full setup and migration instructions.

## Usage

### Analyze Audio Files

Run batch analysis of your `.wav` recordings (requires BirdNET models installed):

```bash
python backend/services/run_audio_analysis.py
```

This will analyze all `.wav` files inside the `./recordings/YYYYMMDD/` folder and output detection results to `./outputs/`.

### Generate Bird Thumbnail (Developer Testing)

This was primarily used to test thumbnail generation. It will be integrated into the web app pipeline in production.

```bash
python backend/services/generate_thumbnail.py "Savannah Sparrow"
```

## Testing

SoundBird includes unit tests to verify core functionality, especially around database interactions and audio analysis logic.

### Test Structure

Tests are located in the `backend/tests/` directory and follow the structure of the main application:

- `tests/repositories/test_detection_repository.py`: Tests for detection repository methods like `save_detections`, `get_detection`, and `delete_detection`.
- Future tests may cover:
  - Input validation for `DetectionCreate`
  - Error handling in audio analysis
  - API route behavior using FastAPI’s `TestClient`

### Running Tests

To run all tests using `pytest`:

```bash
cd backend
pytest -v

## Requirements

- Python 3.10 or 3.11
- Packages listed in `requirements.txt`
- OpenAI API key for DALL-E 3

## Future Work

**SoundBird** is under active development, with the following planned enhancements:

- **Biodiversity Comparison Tools**
  Analyze and compare bird biodiversity levels between different habitats (e.g., old-growth forests vs second-growth) by overlaying spatial data such as GeoJSON habitat boundaries with recording locations.

- **Conservation Alerts**
  Implement an alert system to flag the detection of endangered or species-at-risk in uploaded recordings, based on conservation status databases.

- **Historical and Seasonal Trends**
  Expand functionality to track changes in species presence over time (e.g., year-over-year or seasonal migration patterns).

- **Enhanced Frontend Visualization**
  Integrate map-based exploration, detection timelines, habitat overlays, and rich species profiles, making biodiversity data more intuitive and accessible.

- **Scalable Cloud Processing**
  Expand infrastructure to handle large recording datasets and support collaborative research projects.

- **Community Sharing and Storytelling**
  Allow users to share notable detections, species highlights, and field reports directly through the platform.

## About the Developer

This project is part of an independent R&D initiative focused on combining bioacoustics, machine learning, and generative AI to make biodiversity research more accessible and inspiring.
SoundBird is developed and maintained by Austen Sorochak — a software developer, environmental scientist, and nature enthusiast passionate about connecting technology with the living world.

## Acknowledgements

SoundBird uses the following open-source tools and models:

- [birdnetlib](https://github.com/kahst/birdnetlib) — a Python wrapper for BirdNET-Analyzer, licensed under the Apache License 2.0.
- [BirdNET-Analyzer](https://github.com/kahst/BirdNET-Analyzer) — the underlying species detection engine, source code licensed under the MIT License.
- BirdNET-Analyzer pre-trained models — provided for research and educational use under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

We gratefully acknowledge the BirdNET project's contributions to bioacoustic research and open science.

## License

This project is licensed under the MIT License.
```
