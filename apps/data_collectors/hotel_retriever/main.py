from fastapi import FastAPI, HTTPException, Body
import base64
from typing import List, Optional, Dict, Any
from datetime import datetime
from .data_processor import transform_hotel_data
import redis.asyncio as redis
import json
import os
from dotenv import load_dotenv

from shared.data_types import hotel_pb2
from google.protobuf.json_format import MessageToDict, ParseDict

from liteapi import LiteApi 

app = FastAPI(title="Hotel Data Service")

load_dotenv()

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

# Initialize Hotels API SDK
API_KEY = os.getenv("LITE_API_KEY", "")
api = LiteApi(api_key=API_KEY)

# Cache TTL (1 hour)
CACHE_TTL = 3600

# Redis operations
async def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client


async def cache_get(key: str) -> Optional[Dict]:
    """Get data from Redis cache"""
    try:
        client = await get_redis_client()
        data = await client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


async def cache_set(key: str, value: Dict, ttl: int = CACHE_TTL):
    """Set data in Redis cache"""
    try:
        client = await get_redis_client()
        await client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"Cache set error: {e}")


# API endpoints
@app.on_event("startup")
async def startup():
    """Initialize connections on startup"""
    await get_redis_client()
    print("Redis connection initialized")


@app.on_event("shutdown")
async def shutdown():
    """Close connections on shutdown"""
    if redis_client:
        await redis_client.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/hotels/search")
async def search_hotels(
    payload: str = Body(..., description="Base64-encoded JSON search request")
):
    """
    Search for hotels using a Base64-encoded JSON payload.
    Returns protobuf-compatible JSON.
    """
    # Decode Base64
    try:
        decoded_bytes = base64.b64decode(payload)
        query: Dict[str, Any] = json.loads(decoded_bytes.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {e}")

    # Extract parameters with defaults
    city: str = query["city"]
    country: str = query["country"]
    start_date: str = query["start_date"]
    end_date: str = query["end_date"]

    guests: int = query.get("guests", 1)
    rooms: int = query.get("rooms", 1)
    preferences: List[int] = query.get("preferences", [])
    max_results: int = query.get("max_results", 50)
    max_price_per_night: Optional[float] = query.get("max_price_per_night")
    min_rating: Optional[float] = query.get("min_rating")
    
    try:
        # Use SDK to fetch hotels
        hotel_data = api.get_hotels(
            country_code=country,
            city_name=city,
            limit=max_results
        )
        print(hotel_data)
        
        hotels = hotel_data.get("data", [])
        
        # Get provider from response metadata or default
        provider = hotel_data.get("provider", "Hotels API")
            
        # Create response protobuf
        response = hotel_pb2.HotelSearchResponse()
        
        # Process each hotel
        for hotel in hotels:
            # Filter by rating if specified
            if min_rating and hotel.get("rating", 0) < min_rating:
                continue
            
            hotel_id = hotel.get("id")
            if not hotel_id:
                continue
            
            # Check cache first using hotel ID
            cache_key = f"hotel:{hotel_id}"
            cached_hotel = await cache_get(cache_key)
            
            if cached_hotel:
                print(f"Cache hit for hotel {hotel_id}")
                # Parse cached data back to protobuf
                hotel_option = hotel_pb2.HotelOption()
                ParseDict(cached_hotel, hotel_option)
                
                # Filter by max price if specified
                if max_price_per_night and hotel_option.price_per_night.amount > max_price_per_night:
                    continue
                
                response.options.append(hotel_option)
            else:
                print(f"Cache miss for hotel {hotel_id}")
                
                # Use SDK to fetch room data
                room_data = None
                try:
                    room_details = api.get_hotel_details(hotel_id=hotel_id)
                    # Assuming room details returns rooms list
                    if isinstance(room_details, dict):
                        rooms_list = room_details.get("rooms", [])
                    elif isinstance(room_details, list):
                        rooms_list = room_details
                    else:
                        rooms_list = []
                    
                    if rooms_list:
                        room_data = rooms_list[0]
                except Exception as e:
                    print(f"Error fetching room data for {hotel_id}: {e}")
                
                # Transform hotel data
                hotel_option = transform_hotel_data(
                    hotel, 
                    room_data, 
                    start_date, 
                    end_date, 
                    preferences,
                    provider
                )
                
                # Filter by max price if specified
                if max_price_per_night and hotel_option.price_per_night.amount > max_price_per_night:
                    continue
                
                # Cache the hotel option using hotel ID
                hotel_dict = MessageToDict(hotel_option)
                await cache_set(cache_key, hotel_dict)
                
                response.options.append(hotel_option)
        
        # Set metadata
        search_id = f"search_{datetime.utcnow().timestamp()}"
        response.metadata.total_results = hotel_data.get("total", len(response.options))
        response.metadata.search_id = search_id
        response.metadata.timestamp = datetime.utcnow().isoformat()
        response.metadata.data_source = provider
        
        # Convert to dict for JSON response
        return MessageToDict(response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hotels: {str(e)}")


@app.get("/api/hotels/{hotel_id}")
async def get_hotel_details(hotel_id: str):
    """Get detailed information for a specific hotel"""
    
    # Use hotel ID as cache key
    cache_key = f"hotel:{hotel_id}"
    
    # Try cache first
    cached = await cache_get(cache_key)
    if cached:
        print(f"Cache hit for hotel {hotel_id}")
        return cached
    
    print(f"Cache miss for hotel {hotel_id}")
    
    # Use SDK to fetch from API
    try:
        # Get hotel details using SDK
        hotel_details = api.get_hotel_details(hotel_id=hotel_id)
        
        result = {
            "hotel": hotel_details.get("hotel", hotel_details),
            "rooms": hotel_details.get("rooms", [])
        }
        
        # Cache using hotel ID
        await cache_set(cache_key, result)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SDK error: {str(e)}")


@app.delete("/api/cache/hotel/{hotel_id}")
async def invalidate_hotel_cache(hotel_id: str):
    """Invalidate cache for a specific hotel"""
    try:
        cache_key = f"hotel:{hotel_id}"
        client = await get_redis_client()
        deleted = await client.delete(cache_key)
        return {"deleted": bool(deleted), "hotel_id": hotel_id, "key": cache_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 