# main.py

# Standard library
import os
import logging
from contextlib import asynccontextmanager

# Third-party
from fastapi import FastAPI
from birdnetlib.analyzer import Analyzer

# Internal
from database.config import DATABASE_URL
from backend.app.routes.analyze import router as analyze_router
from backend.app.routes.detections import router as detections_router
from contextlib import asynccontextmanager
import logging

# Debug print for DATABASE_URL environment
print("FASTAPI ENV: ", os.getenv("DATABASE_URL"))

# Configure logging
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

# Register routers
app.include_router(analyze_router, prefix="/api")
app.include_router(detections_router, prefix="/api")
