"""
FastAPI service for all vacation planning data types.
Accepts base64-encoded JSON queries and returns JSON responses.
"""

from fastapi import FastAPI, Query, HTTPException
from typing import Optional, Dict, Any
import json
import base64

# Import your proto files
import shared.data_types.activity_pb2 as activity_types
import shared.data_types.flight_pb2 as flight_types
import shared.data_types.common_pb2 as common_types
import shared.data_types.hotel_pb2 as hotel_types
import shared.data_types.transport_pb2 as transport_types

from apps.data_collectors.llm_data_retriever import generate_json_from_proto

from apps.data_collectors.llm_provider import LLMProvider

app = FastAPI(
    title="Vacation Planning Service",
    description="AI-powered vacation planning data for flights, hotels, activities, and transport",
    version="1.0.0"
)


def decode_json(base64_string: str) -> Dict[str, Any]:
    """
    Decode base64 string to JSON dict.
    
    Args:
        base64_string: Base64 encoded JSON string
    
    Returns:
        Parsed JSON as dictionary
    
    Raises:
        HTTPException: If decoding fails
    """
    try:
        json_bytes = base64.b64decode(base64_string)
        json_string = json_bytes.decode('utf-8')
        return json.loads(json_string)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 JSON: {e}")


# ===== Health Check =====

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vacation-planning"}


# ===== Flight Endpoints =====

@app.get("/get_flight_data")
async def get_flight_data(
    query: str = Query(..., description="Base64 encoded JSON flight query"),
    list_size: Optional[int] = 5
):
    """
    Retrieve flight options based on search parameters.
    
    Query parameters:
    - query: Base64 encoded JSON with flight search parameters
    - list_size: Number of flight options to generate (default: 5)
    
    Example JSON query:
    {
        "origin": {"city": "New York", "airport_code": "JFK"},
        "destination": {"city": "London", "airport_code": "LHR"},
        "departure_date": "2025-03-15",
        "return_date": "2025-03-22",
        "passengers": 2,
        "cabin_class": "economy",
        "preferences": ["BUDGET"]
    }
    
    Returns:
        JSON array of Flight objects
    """
    flight_query = decode_json(query)
    
    print(f"Flight Query: {json.dumps(flight_query, indent=2)}")
    
    resp = generate_json_from_proto(
        proto_cls=flight_types.FlightSegment,
        preferences=flight_query,
        system_description="""
Generate realistic flight options with:
- Real airline names and routes (United, Delta, American, British Airways, etc.)
- Appropriate pricing for cabin class (economy $200-800, business $1000-3000, first $1500-5000)
- Realistic flight durations based on distance
- 0-2 stops for most routes
- ISO 8601 datetime formats (YYYY-MM-DDTHH:MM:SS)
- Realistic layovers when stops > 0
- Amenities appropriate to cabin class
- Component scores between 0.0-1.0
        """,
        list_size=list_size
    )
    
    print(f"Flight Response: {json.dumps(resp, indent=2)}")
    return resp


# ===== Hotel Endpoints =====

@app.get("/get_hotel_data")
async def get_hotel_data(
    query: str = Query(..., description="Base64 encoded JSON hotel query"),
    list_size: Optional[int] = 10
):
    """
    Retrieve hotel options based on search parameters.
    
    Query parameters:
    - query: Base64 encoded JSON with hotel search parameters
    - list_size: Number of hotel options to generate (default: 10)
    
    Example JSON query:
    {
        "location": {"city": "Paris", "country": "France"},
        "check_in": "2025-03-15",
        "check_out": "2025-03-20",
        "guests": 2,
        "rooms": 1,
        "preferences": ["LUXURY", "ROMANTIC"],
        "min_rating": 4.0
    }
    
    Returns:
        JSON array of Hotel objects
    """
    hotel_query = decode_json(query)
    
    print(f"Hotel Query: {json.dumps(hotel_query, indent=2)}")
    
    resp = generate_json_from_proto(
        proto_cls=hotel_types.HotelOption,
        preferences=hotel_query,
        system_description="""
Generate realistic hotel options with:
- Real hotel chains and names (Marriott, Hilton, Hyatt, InterContinental, etc.)
- Appropriate pricing for category: budget $50-100, midscale $100-250, upscale $250-500, luxury $500+
- Ratings 3.0-5.0 with realistic review counts (higher ratings for luxury)
- Star ratings 1-5 (correlate with category)
- Distance to city center: 0.5-5km
- Realistic amenities for category (wifi, pool, gym, spa, etc.)
- Room types: standard, deluxe, suite with bed configurations
- ISO 8601 date format (YYYY-MM-DD)
- Component scores between 0.0-1.0
        """,
        list_size=list_size
    )
    
    print(f"Hotel Response: {json.dumps(resp, indent=2)}")
    return resp


# ===== Activity Endpoints =====

@app.get("/get_activity_data")
async def get_activity_data(
    query: str = Query(..., description="Base64 encoded JSON activity query"),
    list_size: Optional[int] = 15
):
    """
    Retrieve activity options based on search parameters.
    
    Query parameters:
    - query: Base64 encoded JSON with activity search parameters
    - list_size: Number of activity options to generate (default: 15)
    
    Example JSON query:
    {
        "location": {"city": "Tokyo", "country": "Japan"},
        "start_date": "2025-04-01",
        "end_date": "2025-04-07",
        "preferences": ["CULTURE", "FOOD"],
        "categories": ["TOUR", "FOOD_TOUR", "MUSEUM"],
        "max_price": 200
    }
    
    Returns:
        JSON array of Activity objects
    """
    activity_query = decode_json(query)
    
    print(f"Activity Query: {json.dumps(activity_query, indent=2)}")
    
    resp = generate_json_from_proto(
        proto_cls=activity_types.ActivityOption,
        preferences=activity_query,
        system_description="""
Generate realistic activity options with:
- Location-appropriate tours and experiences (match the city/country culture)
- Pricing $10-300 based on activity type (tours $50-150, museums $15-30, food tours $80-200)
- Ratings 3.5-5.0 with realistic review counts
- Duration 60-480 minutes (1-8 hours typically)
- Available time slots with ISO 8601 format (date: YYYY-MM-DD, time: HH:MM)
- Realistic highlights, inclusions, and exclusions
- Difficulty levels: easy, moderate, challenging
- Hotel pickup availability, meal inclusions, cancellation policy
- Component scores between 0.0-1.0
        """,
        list_size=list_size
    )
    
    print(f"Activity Response: {json.dumps(resp, indent=2)}")
    return resp


# ===== Transport Endpoints =====

@app.get("/get_transport_data")
async def get_transport_data(
    query: str = Query(..., description="Base64 encoded JSON transport query"),
    list_size: Optional[int] = 10
):
    """
    Retrieve transport options based on search parameters.
    
    Query parameters:
    - query: Base64 encoded JSON with transport search parameters
    - list_size: Number of transport options to generate (default: 10)
    
    Example JSON query:
    {
        "origin": {"city": "Los Angeles", "country": "USA"},
        "destination": {"city": "San Diego", "country": "USA"},
        "date": "2025-05-10",
        "time": "09:00",
        "passengers": 2,
        "preferred_modes": ["RENTAL_CAR", "TRAIN"]
    }
    
    Returns:
        JSON array of Transport objects
    """
    transport_query = decode_json(query)
    
    print(f"Transport Query: {json.dumps(transport_query, indent=2)}")
    
    resp = generate_json_from_proto(
        proto_cls=transport_types.TransportOption,
        preferences=transport_query,
        system_description="""
Generate realistic transport options with:
- Appropriate modes for distance: <50km rideshare/taxi, 50-200km rental car/train, >200km train/bus
- Real providers: Hertz/Enterprise/Avis for rentals, Uber/Lyft for rides, Amtrak/Greyhound for transit
- Distance-appropriate pricing: rentals $40-100/day, rides $20-150, trains $30-200
- Realistic durations based on mode and distance
- Vehicle/transit details: class, model, seats, features, service class
- ISO 8601 datetime formats (YYYY-MM-DDTHH:MM:SS)
- For rental cars: economy, compact, SUV classes with daily rates and insurance
- For rideshare: sedan, SUV, van options with estimated wait times
- For transit: line numbers, stops, transfers, amenities (wifi, food service)
- Component scores between 0.0-1.0
        """,
        list_size=list_size
    )
    
    print(f"Transport Response: {json.dumps(resp, indent=2)}")
    return resp


# ===== Combined Search Endpoint =====

@app.post("/search_vacation_package")
async def search_vacation_package(
    flight_query: Optional[str] = Query(None, description="Base64 encoded JSON flight query"),
    hotel_query: Optional[str] = Query(None, description="Base64 encoded JSON hotel query"),
    activity_query: Optional[str] = Query(None, description="Base64 encoded JSON activity query"),
    transport_query: Optional[str] = Query(None, description="Base64 encoded JSON transport query"),
    list_size: Optional[int] = 5
):
    """
    Search for a complete vacation package with multiple components.
    
    Query parameters:
    - flight_query: Optional base64 encoded JSON flight query
    - hotel_query: Optional base64 encoded JSON hotel query
    - activity_query: Optional base64 encoded JSON activity query
    - transport_query: Optional base64 encoded JSON transport query
    - list_size: Number of options per category
    
    Returns:
        JSON object with flights, hotels, activities, and transport arrays
    """
    results = {}
    
    if flight_query:
        query_dict = decode_json(flight_query)
        results["flights"] = generate_json_from_proto(
            proto_cls=flight_types.FlightSegment,
            preferences=query_dict,
            system_description="Generate realistic flight options.",
            list_size=list_size,
            provider=LLMProvider.PERPLEXITY
        )
    
    if hotel_query:
        query_dict = decode_json(hotel_query)
        results["hotels"] = generate_json_from_proto(
            proto_cls=hotel_types.HotelOption,
            preferences=query_dict,
            system_description="Generate realistic hotel options.",
            list_size=list_size,
            provider=LLMProvider.PERPLEXITY
        )
    
    if activity_query:
        query_dict = decode_json(activity_query)
        results["activities"] = generate_json_from_proto(
            proto_cls=activity_types.ActivityOption,
            preferences=query_dict,
            system_description="Generate realistic activity options.",
            list_size=list_size,
            provider=LLMProvider.PERPLEXITY
        )
    
    if transport_query:
        query_dict = decode_json(transport_query)
        results["transport"] = generate_json_from_proto(
            proto_cls=transport_types.TransportOption,
            preferences=query_dict,
            system_description="Generate realistic transport options.",
            list_size=list_size,
            provider=LLMProvider.PERPLEXITY
        )
    
    if not results:
        raise HTTPException(status_code=400, detail="At least one query type must be provided")
    
    return results


# ===== Info Endpoint =====

@app.get("/")
def root():
    """Service information and available endpoints"""
    return {
        "service": "Vacation Planning Service",
        "version": "1.0.0",
        "endpoints": {
            "flights": "/get_flight_data",
            "hotels": "/get_hotel_data",
            "activities": "/get_activity_data",
            "transport": "/get_transport_data",
            "package": "/search_vacation_package",
            "health": "/health",
            "docs": "/docs"
        },
        "usage": {
            "description": "Send base64-encoded JSON queries as query parameters",
            "encoding_example": {
                "python": """
import base64
import json

query = {"origin": {"city": "NYC"}, "destination": {"city": "LAX"}}
encoded = base64.b64encode(json.dumps(query).encode()).decode()
# Use 'encoded' as the query parameter
                """,
                "curl": """
# 1. Create JSON file: query.json
# 2. Encode: ENCODED=$(cat query.json | base64)
# 3. Request: curl "http://localhost:8000/get_flight_data?query=$ENCODED&list_size=5"
                """
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)