import os
import json
import re
import redis.asyncio as redis
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timezone, timedelta
from shared.data_types.models import *
from fastapi import FastAPI, HTTPException, Body, Request
from amadeus import Client, ResponseError
from dotenv import load_dotenv
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from .data_processor import transform_flight_data, generate_unique_flight_id
from .default_flights import get_default_flights_by_route, get_default_flight_by_id

# ----------------------------
# Config
# ----------------------------

load_dotenv()

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

# Cache TTL (2 hours for flight data as it's more volatile than hotels)
FLIGHT_CACHE_TTL = 7200

async def get_redis_client():
    global redis_client
    if redis_client is None:
        try:
            redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.info(f"Redis connection error: {e}")
            return None
    return redis_client

async def cache_get(key: str) -> Optional[Dict]:
    try:
        client = await get_redis_client()
        if not client: return None
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.info(f"Cache get error: {e}")
        return None

async def cache_set(key: str, value: Dict, ttl: int = FLIGHT_CACHE_TTL):
    try:
        client = await get_redis_client()
        await client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.info(f"Cache set error: {e}")

async def map_provider_id(unique_id: str, provider_offer: Dict):
    """Map generated unique ID to raw provider offer data"""
    try:
        client = await get_redis_client()
        if not client: return
        key = f"map:flight_offer:{unique_id}"
        await client.setex(key, FLIGHT_CACHE_TTL * 3, json.dumps(provider_offer))
    except Exception as e:
        logger.info(f"Mapping error: {e}")

async def get_provider_offer(unique_id: str) -> Optional[Dict]:
    """Get raw provider offer from unique ID"""
    try:
        client = await get_redis_client()
        if not client: return None
        key = f"map:flight_offer:{unique_id}"
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.info(f"Mapping lookup error: {e}")
        return None

# Amadeus Client
amadeus = None
if AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET:
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

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Handled {request.method} {request.url.path} in {duration:.4f} seconds")
    return response

@app.on_event("startup")
async def startup():
    await get_redis_client()
    logger.info("Startup: Service initialized")

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()

@app.post("/api/flight_retriever/search", response_model=FlightSearchResponse)
async def flight_search(request: FlightSearchRequest):

    origin_code = (request.origin.airport_code or "").strip().upper()
    dest_code = (request.destination.airport_code or "").strip().upper()
    departure_date = (request.departure_date or "").strip()
    adults = max(1, int(request.passengers or 1))

    # Try to resolve codes from city names if missing
    if not origin_code and request.origin.city:
        from .default_flights import get_airport_code_for_city
        origin_code = (get_airport_code_for_city(request.origin.city) or "").upper()
        
    if not dest_code and request.destination.city:
        from .default_flights import get_airport_code_for_city
        dest_code = (get_airport_code_for_city(request.destination.city) or "").upper()

    # Try API if configured and codes are present
    if amadeus and origin_code and dest_code and departure_date:
        try:
            # Check if entire search is cached
            search_cache_key = f"flight_search:{origin_code}:{dest_code}:{departure_date}:{adults}"
            cached_response = await cache_get(search_cache_key)
            if cached_response:
                return FlightSearchResponse.model_validate(cached_response)

            logger.info(f"Calling Amadeus for {origin_code}->{dest_code}...")
            resp = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin_code,
                destinationLocationCode=dest_code,
                departureDate=departure_date,
                adults=adults,
                max=250,
            )

            result = getattr(resp, "result", None) or {}
            dictionaries = result.get("dictionaries", {}) or {}
            locations = dictionaries.get("locations", {}) or {}
            offers = resp.data or []

            flight_options: List[FlightOption] = []
            for o in offers:
                itineraries = o.get("itineraries", []) or []
                segments = itineraries[0].get("segments", []) if itineraries else []
                unique_id = generate_unique_flight_id(segments)

                opt_cache_key = f"flight_option:{unique_id}"
                cached_opt = await cache_get(opt_cache_key)
                
                if cached_opt:
                    opt = FlightOption.model_validate(cached_opt)
                else:
                    opt = transform_flight_data(o, passengers=adults, locations=locations)
                    await cache_set(opt_cache_key, opt.model_dump())
                
                await map_provider_id(unique_id, o)
                flight_options.append(opt)

            metadata = SearchMetadata(
                total_results=len(flight_options),
                search_id=f"flight_search_{datetime.now(timezone.utc).timestamp()}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                data_source="Amadeus",
            )

            response = FlightSearchResponse(options=flight_options, metadata=metadata)
            await cache_set(search_cache_key, response.model_dump())
            return response

        except (ResponseError, Exception) as e:
            logger.info(f"Amadeus API error: {e}. Falling back to default flights.")
    else:
        logger.info("Amadeus not configured. Falling back to default flights.")

    # FALLBACK: Use default_flights generator
    try:
        default_flights_data = get_default_flights_by_route(
            origin_city=request.origin.city,
            destination_city=request.destination.city,
            origin_code=origin_code,
            dest_code=dest_code,
            departure_date=departure_date,
            passengers=adults
        )

        flight_options = [FlightOption.model_validate(f) for f in default_flights_data]
        
        metadata = SearchMetadata(
            total_results=len(flight_options),
            search_id=f"default_flight_search_{datetime.now(timezone.utc).timestamp()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="Default Flight Generator",
        )
        
        return FlightSearchResponse(options=flight_options, metadata=metadata)
    except Exception as fe:
        logger.info(f"Fallback generation error: {fe}")
        raise HTTPException(status_code=502, detail=f"Flight service unavailable: {fe}")

@app.get("/api/flight_retriever/flights/{flight_id}")
async def get_flight_details(flight_id: str):
    """Get raw offer details from provider using unique mapping or default data"""
    if flight_id.startswith("default_f_") or flight_id.startswith("mock_f_"):
        default_flight = get_default_flight_by_id(flight_id)
        if default_flight:
            return default_flight
            
    offer = await get_provider_offer(flight_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Flight offer not found in cache or expired")
    return offer

@app.post("/api/flight_retriever/flights/{flight_id}/price")
async def verify_price(flight_id: str):
    """Verify current price and availability for a flight offer or default data"""
    if flight_id.startswith("default_f_") or flight_id.startswith("mock_f_"):
        default_flight = get_default_flight_by_id(flight_id)
        if default_flight:
            return {"data": default_flight, "status": "verified", "source": "mock_data"}

    offer = await get_provider_offer(flight_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Flight offer not found in cache or expired")
    
    if not amadeus:
        return {"data": transform_flight_data(offer), "status": "verified", "source": "cached_offline"}

    try:
        price_resp = amadeus.shopping.flight_offers.pricing.post(offer)
        return price_resp.result
    except ResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
