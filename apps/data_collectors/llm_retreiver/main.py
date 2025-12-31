"""
FastAPI service for all vacation planning data types.
Accepts JSON requests and returns JSON responses.
"""

from fastapi import FastAPI, HTTPException, Body
from typing import Optional, Dict, Any
import json

# Import proto files
import shared.data_types.activity_pb2 as activity_types
import shared.data_types.flight_pb2 as flight_types
import shared.data_types.hotel_pb2 as hotel_types
import shared.data_types.transport_pb2 as transport_types

from apps.data_collectors.llm_retreiver.llm_data_retriever import (
    generate_json_from_proto
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


# ===== Flights =====

@app.post("/flights/search")
async def get_flight_data(
    query: Dict[str, Any] = Body(..., description="Flight search JSON"),
    list_size: int = 5
):
    resp = generate_json_from_proto(
        proto_cls=flight_types.FlightSegment,
        preferences=query,
        system_description="""
Generate realistic flight options with:
- Real airline names and routes
- Appropriate pricing by cabin class
- ISO 8601 datetime formats
- 0–2 stops
- Component scores between 0.0–1.0
        """,
        list_size=list_size
    )
    return resp


# ===== Activities =====

@app.post("/activities/search")
async def get_activity_data(
    query: Dict[str, Any] = Body(..., description="Activity search JSON"),
    list_size: int = 15
):
    resp = generate_json_from_proto(
        proto_cls=activity_types.ActivityOption,
        preferences=query,
        system_description="""
Generate realistic activity options:
- City-specific experiences
- Duration 1–8 hours
- Prices $10–300
- Ratings & highlights
        """,
        list_size=list_size
    )
    return resp


# ===== Transport =====

@app.post("/transport/search")
async def get_transport_data(
    query: Dict[str, Any] = Body(..., description="Transport search JSON"),
    list_size: int = 10
):
    resp = generate_json_from_proto(
        proto_cls=transport_types.TransportOption,
        preferences=query,
        system_description="""
Generate realistic transport options:
- Distance-appropriate modes
- Real providers
- ISO 8601 datetime
- Component scores
        """,
        list_size=list_size
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