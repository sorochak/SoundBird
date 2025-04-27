# main.py
from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI()


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint to verify if the server is running.
    Returns:
        dict: A simple message indicating the server is running.
    """
    return {"status": "OK", "message": "Server is running."}
