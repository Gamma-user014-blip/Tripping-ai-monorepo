"""
FastAPI service for all vacation planning data types.
Accepts JSON requests and returns JSON responses.
"""

from fastapi import FastAPI, HTTPException, Body, Request
from typing import Optional, Dict, Any
import json
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Pydantic models
from shared.data_types import models

from apps.data_collectors.llm_retreiver.llm_data_retriever import (
    generate_json_from_model
)
from apps.data_collectors.llm_retreiver.llm_provider import LLMProvider

app = FastAPI(
    title="Vacation Planning Service",
    description="AI-powered vacation planning data for flights, hotels, activities, and transport",
    version="1.1.0"
)

# ===== Health Check =====

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "vacation-planning"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Handled {request.method} {request.url.path} in {duration:.4f} seconds")
    return response


# ===== Flights =====

@app.post("/api/flights/search", response_model=models.FlightSearchResponse)
async def get_flight_data(
    query: models.FlightSearchRequest = Body(..., description="Flight search request")
):
    resp = generate_json_from_model(
        model_cls=models.FlightSearchResponse,
        preferences=query.model_dump(),
        list_size=query.max_results or 5
    )
    return resp


# ===== Activities =====

@app.post("/api/activities/search", response_model=models.ActivitySearchResponse)
async def get_activity_data(
    query: models.ActivitySearchRequest = Body(..., description="Activity search request")
):
    logger.info("Searching activities...")
    resp = generate_json_from_model(
        model_cls=models.ActivitySearchResponse,
        preferences=query.model_dump(),
        list_size=query.max_results or 15
    )
    logger.info("Activity search returned")

    return resp


# ===== Transport =====

@app.post("/api/transport/search", response_model=models.TransportSearchResponse)
async def get_transport_data(
    query: models.TransportSearchRequest = Body(..., description="Transport search request")
):
    resp = generate_json_from_model(
        model_cls=models.TransportSearchResponse,
        preferences=query.model_dump(),
        list_size=query.max_results or 10
    )
    return resp


# ===== Root =====

@app.get("/")
def root():
    return {
        "service": "Vacation Planning Service",
        "version": "1.1.0",
        "endpoints": {
            "flights": "POST /flights/search",
            "activities": "POST /activities/search",
            "transport": "POST /transport/search",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
