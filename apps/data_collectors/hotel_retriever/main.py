from fastapi import FastAPI, HTTPException, Body
import base64
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from .data_processor import transform_hotel_data, generate_unique_hotel_id
import redis.asyncio as redis
import json
import os
from dotenv import load_dotenv

from shared.data_types import models

from .custom_liteapi import CustomLiteApi

app = FastAPI(title="Hotel Data Service")

load_dotenv()

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

# Initialize Custom Hotels API SDK
API_KEY = os.getenv("LITE_API_KEY", "")

api = CustomLiteApi(api_key=API_KEY)

# Cache TTL (1 hour for hotel data, 30 minutes for availability)
HOTEL_CACHE_TTL = 3600
AVAILABILITY_CACHE_TTL = 1800

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


async def cache_set(key: str, value: Dict, ttl: int = HOTEL_CACHE_TTL):
    """Set data in Redis cache"""
    try:
        client = await get_redis_client()
        await client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"Cache set error: {e}")


async def map_provider_id(unique_id: str, provider_id: str):
    """Map generated unique ID to provider ID"""
    try:
        client = await get_redis_client()
        key = f"map:provider_id:{unique_id}"
        await client.setex(key, HOTEL_CACHE_TTL * 24, provider_id) # Keep mapping longer
    except Exception as e:
        print(f"Mapping error: {e}")


async def get_provider_id(unique_id: str) -> Optional[str]:
    """Get provider ID from unique ID"""
    try:
        client = await get_redis_client()
        key = f"map:provider_id:{unique_id}"
        return await client.get(key)
    except Exception as e:
        print(f"Mapping lookup error: {e}")
        return None


def build_occupancies(guests: int, rooms: int, children_ages: List[int] = None) -> List[Dict]:
    """Build occupancy structure for API request"""
    if children_ages is None:
        children_ages = []
    
    occupancies = []
    adults_per_room = max(1, guests // rooms)
    
    for i in range(rooms):
        occupancy = {
            "rooms": 1,
            "adults": adults_per_room
        }
        
        # Distribute children across rooms if any
        if children_ages and i == 0:
            occupancy["children"] = children_ages
        
        occupancies.append(occupancy)
    
    return occupancies


async def check_hotel_availability(
    hotel_id: str,
    checkin: str,
    checkout: str,
    guests: int,
    rooms: int,
    currency: str = "USD",
    guest_nationality: str = "US",
    unique_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Check hotel availability and get rates for specific dates
    Returns availability data or None if not available
    """
    # Build cache key for availability
    # Use unique_id for caching if provided, otherwise fallback to provider hotel_id
    cache_id = unique_id if unique_id else hotel_id
    availability_cache_key = f"availability:{cache_id}:{checkin}:{checkout}:{guests}:{rooms}"
    
    # Check cache first
    cached_availability = await cache_get(availability_cache_key)
    if cached_availability:
        print(f"Cache hit for availability {cache_id} ({checkin} to {checkout})")
        return cached_availability
    
    print(f"Cache miss for availability {cache_id} ({checkin} to {checkout})")
    
    try:
        # Build occupancies
        occupancies = build_occupancies(guests, rooms)
        
        # Call rates API to check availability
        rates_response = api.get_rates(
            hotel_ids=[hotel_id],
            checkin=checkin,
            checkout=checkout,
            currency=currency,
            guest_nationality=guest_nationality,
            occupancies=occupancies
        )
        
        # Check if we got valid data
        if not rates_response or "data" not in rates_response:
            return None
        
        # Check for errors
        if "error" in rates_response:
            print(f"No availability for {hotel_id}: {rates_response['error'].get('message')}")
            return None
        
        hotel_rates = rates_response["data"]
        if not hotel_rates or len(hotel_rates) == 0:
            return None
        
        # Get the first hotel's rate data
        hotel_rate_data = hotel_rates[0]
        
        # Check if hotel has room types available
        if "roomTypes" not in hotel_rate_data or len(hotel_rate_data["roomTypes"]) == 0:
            return None
        
        # Cache the availability data (shorter TTL than hotel data)
        await cache_set(availability_cache_key, hotel_rate_data, AVAILABILITY_CACHE_TTL)
        
        return hotel_rate_data
        
    except Exception as e:
        print(f"Error checking availability for {hotel_id}: {e}")
        return None


def extract_room_data_from_availability(availability_data: Dict) -> Optional[Dict]:
    """
    Extract room data from the availability response.
    Uses the best rate's room information.
    """
    if not availability_data or "roomTypes" not in availability_data:
        return None
    
    room_types = availability_data["roomTypes"]
    if not room_types:
        return None
    
    # Find the cheapest room type
    best_room = None
    best_price = float('inf')
    
    for room_type in room_types:
        if "offerRetailRate" in room_type:
            price = room_type["offerRetailRate"].get("amount", float('inf'))
            if price < best_price:
                best_price = price
                best_room = room_type
    
    if not best_room:
        return None
    
    # Get the first rate from the best room type
    rates = best_room.get("rates", [])
    if not rates:
        return None
    
    first_rate = rates[0]
    
    # Build room data structure that matches what data_processor expects
    room_data = {
        "roomName": first_rate.get("name", "Standard Room"),
        "maxOccupancy": first_rate.get("maxOccupancy", 2),
        "adultCount": first_rate.get("adultCount", 2),
        "childCount": first_rate.get("childCount", 0),
        "childrenAges": first_rate.get("childrenAges", []),
        "boardType": first_rate.get("boardType", ""),
        "boardName": first_rate.get("boardName", ""),
        "roomAmenities": []  # Not provided in rates response, use empty list
    }
    
    return room_data


def extract_best_rate(availability_data: Dict) -> Optional[Dict]:
    """
    Extract the best (cheapest) rate from availability data
    Returns rate info with pricing
    """
    if not availability_data or "roomTypes" not in availability_data:
        return None
    
    room_types = availability_data["roomTypes"]
    if not room_types:
        return None
    
    # Find the cheapest room type
    best_room = None
    best_price = float('inf')
    
    for room_type in room_types:
        if "offerRetailRate" in room_type:
            price = room_type["offerRetailRate"].get("amount", float('inf'))
            if price < best_price:
                best_price = price
                best_room = room_type
    
    if not best_room:
        return None
    
    # Extract rate details from first rate in the room type
    rates = best_room.get("rates", [])
    if not rates:
        return None
    
    first_rate = rates[0]
    
    return {
        "room_type_id": best_room.get("roomTypeId"),
        "room_name": first_rate.get("name"),
        "max_occupancy": first_rate.get("maxOccupancy"),
        "board_type": first_rate.get("boardType"),
        "board_name": first_rate.get("boardName"),
        "price": best_room.get("offerRetailRate"),
        "suggested_price": best_room.get("suggestedSellingPrice"),
        "initial_price": best_room.get("offerInitialPrice"),
        "taxes_and_fees": first_rate.get("retailRate", {}).get("taxesAndFees", []),
        "cancellation_policies": first_rate.get("cancellationPolicies"),
        "rate_id": first_rate.get("rateId"),
        "offer_id": best_room.get("offerId"),
        "supplier": best_room.get("supplier"),
        "available": True
    }


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
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/hotels/search")
async def search_hotels(
    query: models.HotelSearchRequest = Body(..., description="Hotel search request")
):
    """
    Search for hotels using a JSON payload.
    Checks availability for given dates and only returns available hotels.
    Returns Pydantic model-compatible JSON.
    """
    # Extract parameters from Pydantic model
    city = query.location.city
    country = query.location.country
    start_date = query.dates.start_date
    end_date = query.dates.end_date

    guests = query.guests or 1
    rooms = query.rooms or 1
    
    # Extract preferences from enum list if present
    preferences = [p.value for p in query.preferences]
    
    max_results = query.max_results or 50
    max_price_per_night = query.max_price_per_night or None
    min_rating = query.min_rating or None
    
    # Defaults not in model but needed for API
    currency = "USD" 
    guest_nationality = "US"
    
    try:
        # Use SDK to fetch hotels in the area
        hotel_data = api.get_hotels(
            country_code=country,
            city_name=city,
            limit=max_results
        )
        print(f"Found {len(hotel_data.get('data', []))} hotels in {city}")
        
        hotels = hotel_data.get("data", [])
        
        # Get provider from response metadata or default
        provider = hotel_data.get("provider", "LiteAPI")
            
        # Create response model
        response = models.HotelSearchResponse()
        
        # Process each hotel and check availability
        available_count = 0
        for hotel in hotels:
            # Filter by rating if specified
            if min_rating and hotel.get("rating", 0) < min_rating:
                continue
            
            hotel_id = hotel.get("id")
            if not hotel_id:
                continue

            # Generate unique global ID
            name = hotel.get("name", "")
            lat = float(hotel.get("latitude", 0.0))
            lon = float(hotel.get("longitude", 0.0))
            unique_id = generate_unique_hotel_id(name, lat, lon)
            
            # Save mapping for later retrieval
            await map_provider_id(unique_id, hotel_id)
            
            # Check cache for transformed hotel data FIRST to avoid API calls
            cache_key = f"hotel:{unique_id}:{start_date}:{end_date}"
            cached_hotel = await cache_get(cache_key)
            
            if cached_hotel:
                print(f"Cache hit for transformed hotel {unique_id}")
                hotel_option = models.HotelOption.model_validate(cached_hotel)
                
                # Filter by max price if specified
                if max_price_per_night and hotel_option.price_per_night.amount > max_price_per_night:
                    continue
                
                response.options.append(hotel_option)
                available_count += 1
                continue # Path optimized: Skip availability API check

            # Cache miss: Check hotel availability for the requested dates
            print(f"Cache miss for transformed hotel {unique_id}, checking live availability...")
            availability_data = await check_hotel_availability(
                hotel_id=hotel_id,
                checkin=start_date,
                checkout=end_date,
                guests=guests,
                rooms=rooms,
                currency=currency,
                guest_nationality=guest_nationality,
                unique_id=unique_id
            )
            
            # Skip if not available
            if not availability_data:
                print(f"Hotel {unique_id} ({hotel_id}) not available for {start_date} to {end_date}")
                continue
            
            # Extract best rate
            best_rate = extract_best_rate(availability_data)
            if not best_rate:
                print(f"No rates found for hotel {unique_id}")
                continue
            
            # Extract room data from the availability response
            room_data = extract_room_data_from_availability(availability_data)
            
            # Transform hotel data with availability info (returns Pydantic model)
            hotel_option = transform_hotel_data(
                hotel, 
                room_data, 
                start_date, 
                end_date, 
                preferences,
                provider,
                best_rate
            )
            
            # Filter by max price if specified
            if max_price_per_night and hotel_option.price_per_night.amount > max_price_per_night:
                continue
            
            # Cache the transformed hotel option
            hotel_dict = hotel_option.model_dump()
            await cache_set(cache_key, hotel_dict, HOTEL_CACHE_TTL)
            
            response.options.append(hotel_option)
            available_count += 1
        
        print(f"Found {available_count} available hotels out of {len(hotels)} total")
        
        # Set metadata
        search_id = f"search_{datetime.now(timezone.utc).timestamp()}"
        response.metadata.total_results = available_count
        response.metadata.search_id = search_id
        response.metadata.timestamp = datetime.now(timezone.utc).isoformat()
        response.metadata.data_source = provider
        
        # Convert to dict for JSON response
        return response.model_dump()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hotels: {str(e)}")


@app.get("/api/hotels/{hotel_id}")
async def get_hotel_details(hotel_id: str):
    """Get detailed information for a specific hotel (basic info only)"""
    
    # Use hotel ID as cache key
    cache_key = f"hotel_details:{hotel_id}"
    
    # Try cache first
    cached = await cache_get(cache_key)
    if cached:
        print(f"Cache hit for hotel details {hotel_id}")
        return cached
    
    print(f"Cache miss for hotel details {hotel_id}")
    
    # Resolve provider ID from unique ID mapping
    provider_id = await get_provider_id(hotel_id)
    if not provider_id:
        print(f"No provider mapping found for {hotel_id}, assuming direct ID")
        provider_id = hotel_id
    
    # Use SDK to fetch from API
    try:
        # Get hotel details using SDK
        hotel_details = api.get_hotel_details(hotel_id=provider_id)
        
        result = {
            "hotel": hotel_details.get("hotel", hotel_details),
            "rooms": hotel_details.get("rooms", [])
        }
        
        # Cache using hotel ID
        await cache_set(cache_key, result, HOTEL_CACHE_TTL)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SDK error: {str(e)}")


@app.post("/api/hotels/{hotel_id}/availability")
async def check_availability(
    hotel_id: str,
    checkin: str = Body(...),
    checkout: str = Body(...),
    guests: int = Body(default=1),
    rooms: int = Body(default=1),
    currency: str = Body(default="USD"),
    guest_nationality: str = Body(default="US")
):
    """
    Check availability and get rates for a specific hotel
    """
    # Resolve provider ID from unique ID mapping
    provider_id = await get_provider_id(hotel_id)
    if not provider_id:
        # Fallback to assuming the passed ID is the provider ID if no mapping found
        # (Useful for direct API usage or testing)
        provider_id = hotel_id
        
    availability_data = await check_hotel_availability(
        hotel_id=provider_id,
        checkin=checkin,
        checkout=checkout,
        guests=guests,
        rooms=rooms,
        currency=currency,
        guest_nationality=guest_nationality,
        unique_id=hotel_id  # Cache using the request ID (UUID)
    )
    
    if not availability_data:
        raise HTTPException(status_code=404, detail="No availability found for this hotel")
    
    return availability_data


@app.delete("/api/cache/hotel/{hotel_id}")
async def invalidate_hotel_cache(hotel_id: str):
    """Invalidate all cache entries for a specific hotel"""
    try:
        client = await get_redis_client()
        
        # Delete all keys matching the pattern
        pattern = f"hotel:{hotel_id}*"
        cursor = 0
        deleted_count = 0
        
        while True:
            cursor, keys = await client.scan(cursor, match=pattern, count=100)
            if keys:
                deleted_count += await client.delete(*keys)
            if cursor == 0:
                break
        
        # Also delete availability cache
        availability_pattern = f"availability:{hotel_id}*"
        cursor = 0
        
        while True:
            cursor, keys = await client.scan(cursor, match=availability_pattern, count=100)
            if keys:
                deleted_count += await client.delete(*keys)
            if cursor == 0:
                break
        
        return {
            "deleted": deleted_count,
            "hotel_id": hotel_id,
            "message": f"Invalidated {deleted_count} cache entries"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)