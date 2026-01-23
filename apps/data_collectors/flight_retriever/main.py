import os
import json
import redis.asyncio as redis
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timezone 
from shared.data_types.models import *
from fastapi import FastAPI, HTTPException, Body
from amadeus import Client, ResponseError
from dotenv import load_dotenv

from .data_processor import transform_flight_data, generate_unique_flight_id
# ----------------------------
# Config
# ----------------------------

load_dotenv()

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
    raise RuntimeError("Missing Amadeus credentials – check .env")

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

# Cache TTL (2 hours for flight data as it's more volatile than hotels)
FLIGHT_CACHE_TTL = 7200

async def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

async def cache_get(key: str) -> Optional[Dict]:
    try:
        client = await get_redis_client()
        data = await client.get(key)
        if data:
            return json.loads(data)
        print(f"DEBUG: cache_get returning None for key: {key}")
        return None
    except Exception as e:
        print(f"Cache get error: {e}")
        print(f"DEBUG: cache_get returning None due to exception for key: {key}")
        return None

async def cache_set(key: str, value: Dict, ttl: int = FLIGHT_CACHE_TTL):
    try:
        client = await get_redis_client()
        await client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"Cache set error: {e}")

async def map_provider_id(unique_id: str, provider_offer: Dict):
    """Map generated unique ID to raw provider offer data"""
    try:
        client = await get_redis_client()
        key = f"map:flight_offer:{unique_id}"
        # Store the entire raw offer because Amadeus IDs are extremely transient
        await client.setex(key, FLIGHT_CACHE_TTL * 3, json.dumps(provider_offer))
    except Exception as e:
        print(f"Mapping error: {e}")

async def get_provider_offer(unique_id: str) -> Optional[Dict]:
    """Get raw provider offer from unique ID"""
    try:
        client = await get_redis_client()
        key = f"map:flight_offer:{unique_id}"
        data = await client.get(key)
        if data:
            return json.loads(data)
        print(f"DEBUG: get_provider_offer returning None for unique_id: {unique_id}")
        return None
    except Exception as e:
        print(f"Mapping lookup error: {e}")
        print(f"DEBUG: get_provider_offer returning None due to exception for unique_id: {unique_id}")
        return None

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET,
)

app = FastAPI(title="Flight Retriever Service")

# ----------------------------
# FastAPI endpoints
# ----------------------------

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}


@app.on_event("startup")
async def startup():
    await get_redis_client()
    print("Redis connection initialized")

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ----------------------------
# Helpers
# ----------------------------

# Helper functions moved to data_processor.py



@app.post("/api/flight_retriever/search", response_model=FlightSearchResponse)
async def flight_search(request: FlightSearchRequest):

    if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Missing AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET env vars")

    if not request.origin.airport_code or not request.destination.airport_code or not request.departure_date:
        raise HTTPException(
            status_code=400,
            detail="origin.airport_code, destination.airport_code, and departure_date are required",
        )

    origin_code = request.origin.airport_code.strip().upper()
    dest_code = request.destination.airport_code.strip().upper()
    departure_date = request.departure_date.strip()
    adults = max(1, int(request.passengers or 1))

    max_results = 250  # your decision

    try:
        # Check if entire search is cached (Optional, but good for performance)
        search_cache_key = f"flight_search:{origin_code}:{dest_code}:{departure_date}:{adults}"
        cached_response = await cache_get(search_cache_key)
        if cached_response:
            print(f"Cache hit for search {search_cache_key}")
            return FlightSearchResponse.model_validate(cached_response)

        print(f"Cache miss for search {search_cache_key}, calling Amadeus...")
        resp = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=dest_code,
            departureDate=departure_date,
            adults=adults,
            max=max_results,
        )

        result = getattr(resp, "result", None) or {}
        dictionaries = result.get("dictionaries", {}) or {}
        locations = dictionaries.get("locations", {}) or {}
        
        offers = resp.data or []

        flight_options: list[FlightOption] = []
        for o in offers:
            # Generate Unique ID based on segments (before transformation)
            itineraries = o.get("itineraries", []) or []
            segments = itineraries[0].get("segments", []) if itineraries else []
            unique_id = generate_unique_flight_id(segments)

            # Check if THIS INDIVIDUAL flight option is in cache
            # (Matches hotel_retriever pattern)
            opt_cache_key = f"flight_option:{unique_id}"
            cached_opt = await cache_get(opt_cache_key)
            
            if cached_opt:
                # Use cached transformed model
                opt = FlightOption.model_validate(cached_opt)
            else:
                # Transform and cache
                opt = transform_flight_data(o, passengers=adults, locations=locations)
                await cache_set(opt_cache_key, opt.model_dump())
            
            # Save mapping to raw offer for price verification later
            await map_provider_id(unique_id, o)
            flight_options.append(opt)

        # ---- build metadata ----
        metadata = SearchMetadata(
            total_results=len(flight_options),
            search_id=f"flight_search_{datetime.now(timezone.utc).timestamp()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="Amadeus",
        )

        response = FlightSearchResponse(options=flight_options, metadata=metadata)
        
        # Cache the entire search response
        await cache_set(search_cache_key, response.model_dump())

        return response

    except ResponseError as e:
        # Amadeus SDK wraps API errors in ResponseError
        status_code = getattr(e.response, "status_code", 502)
        error_body = getattr(e.response, "body", None) or {}
        errors = error_body.get("errors", []) if isinstance(error_body, dict) else []
        detail_msg = errors[0].get("detail", str(e)) if errors else str(e)
        print(f"Amadeus API error [{status_code}]: {detail_msg}")
        print(f"Full error body: {error_body}")
        raise HTTPException(status_code=status_code, detail=f"Amadeus error: {detail_msg}")
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=502, detail=f"Amadeus error: {e}")


@app.get("/api/flight_retriever/flights/{flight_id}")
async def get_flight_details(flight_id: str):
    """Get raw offer details from provider using unique mapping"""
    offer = await get_provider_offer(flight_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Flight offer not found in cache or expired")
    return offer


@app.post("/api/flight_retriever/flights/{flight_id}/price")
async def verify_price(flight_id: str):
    """Verify current price and availability for a flight offer"""
    offer = await get_provider_offer(flight_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Flight offer not found in cache or expired")
    
    try:
        # Call Amadeus Pricing API to verify
        # Note: This requires the full raw offer object
        price_resp = amadeus.shopping.flight_offers.pricing.post(offer)
        return price_resp.result
    except ResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions moved to data_processor.py or removed if redundant


