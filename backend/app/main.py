# main.py
from fastapi import FastAPI
from birdnetlib.analyzer import Analyzer
from backend.app.routes.analyze import router as analyze_router
from backend.app.routes.detections import router as detections_router
from database.config import Base, engine
from backend.app.models.detection import Detections
from contextlib import asynccontextmanager
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Loading BirdNET analyzer...")
    app.state.analyzer = Analyzer()
    yield
    logging.info("Shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to the SoundBird API. Visit /docs for documentation.",
        "status": "OK",
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint to verify if the server is running.
    Returns:
        dict: A simple message indicating the server is running.
    """
    return {"status": "OK", "message": "Server is running."}


app.include_router(analyze_router, prefix="/api")
app.include_router(detections_router, prefix="/api")
