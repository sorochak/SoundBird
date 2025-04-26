# SoundBird

**SoundBird** is a full-stack web application for analyzing bird audio recordings, detecting species, visualizing biodiversity patterns, and sharing discoveries.

Built for researchers, conservationists, and nature enthusiasts, SoundBird enables users to upload field recordings (e.g., from devices like AudioMoth), automatically detect bird species using machine learning models like BirdNET, and explore the results through an interactive frontend interface.  
The system highlights species presence across time and location, generates AI-assisted species thumbnails, and flags endangered or at-risk species based on detections.

SoundBird is designed to make acoustic biodiversity data more accessible, engaging, and actionable.

SoundBird is currently under active development. It will allow users to:

- Upload recordings from bioacoustic devices like AudioMoth
- Detect bird species using BirdNET
- Generate photorealistic species thumbnails and summaries
- Visualize biodiversity patterns through an interactive frontend
- Explore trends, hotspots, and potential conservation insights

## Current Features

- **Audio Analysis**: Detects bird species in `.wav` recordings using BirdNET.
- **Species Thumbnail Generation**: Generates photorealistic images of detected birds using OpenAI's DALL-E 3.
- **Wikipedia Species Descriptions**: Fetches detailed descriptions to enrich detection results.
- **Output Formats**: Saves analysis results in both `.csv` and `.json` formats.
- **Planned API Integration**: Scripts will be callable via API endpoints in the web app.

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

## Usage

### Analyze Audio Files

Run batch analysis of your `.wav` recordings (requires BirdNET models installed):

```bash
python scripts/run_audio_analysis.py
```

This will analyze all `.wav` files inside the `./recordings/YYYYMMDD/` folder and output detection results to `./outputs/`.

### Generate Bird Thumbnail (Developer Testing)

This was primarily used to test thumbnail generation. It will be integrated into the web app pipeline in production.

```bash
python src/generate_thumbnail.py "American Goldfinch"
```

## Requirements

- Python 3.10 or 3.11
- Packages listed in `requirements.txt`
- OpenAI API key for DALL-E 3

## Future Work

- **Frontend Launch**: Build the first public web interface to upload recordings and explore analysis results.
- **Dynamic Audio/Species Explorer**: View detections by time, location, and species with interactive maps and charts.
- **Database Migration**: Store bird species descriptions, analysis outputs, and generated images in a database.
- **GeoJSON Overlays**: Allow users to compare detected biodiversity across mapped ecosystems (e.g., old growth forests vs. non-old growth).
- **Endangered Species Alerts**: Automatically flag recordings that detect species at risk.
- **User Upload Portal**: Support user-submitted recordings for citizen science projects.
- **Scalability Improvements**: Optimize large batch analyses and cloud deployment.

## License

This project is licensed under the MIT License.
