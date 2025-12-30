from fastapi import FastAPI, HTTPException, Request
from app.schemas import TransitRequest, TransitResponse
from app.transit_service import get_transit_analysis_payload
from app.logger_config import logger
import uvicorn
import time
import os
from dotenv import load_dotenv

# 1. Load environment variables from .env
load_dotenv()

# 2. Initialize the application
app = FastAPI(title=os.getenv("PROJECT_NAME", "AstroMind API"))

# 3. Request logging middleware (optional, but highly useful)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Path: {request.url.path} | Duration: {duration:.4f}s | Status: {response.status_code}")
    return response

# Health monitoring endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring systems"""
    return {
        "status": "ok",
        "engine": "AstroMind",
        "version": "1.0.0"
    }

# 4. Main analysis endpoint
@app.post("/api/v1/analyze", response_model=TransitResponse)
async def analyze_transit(request: TransitRequest):
    try:
        # Business logic for transit calculation
        payload = get_transit_analysis_payload(request.chart_data, request.transit_date)
        return payload
    except Exception as e:
        logger.error(f"Calculation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Calculation Error")

# 5. Entry point
if __name__ == "__main__":
    # Get configuration from .env with default fallback values
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    logger.info(f"Starting {app.title} server on {host}:{port}...")

    # Run via "app.api:app" string format to support hot-reload
    uvicorn.run("app.api:app", host=host, port=port, reload=debug)