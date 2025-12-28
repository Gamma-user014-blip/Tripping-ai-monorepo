from shared.data_types import common_pb2, hotel_pb2
from typing import List, Optional, Dict
from datetime import datetime

def _get_rating_category(rating: float) -> str:
    """Convert numeric rating to category"""
    if rating >= 9.0:
        return "Exceptional"
    elif rating >= 8.0:
        return "Excellent"
    elif rating >= 7.0:
        return "Very Good"
    elif rating >= 6.0:
        return "Good"
    else:
        return "Fair"


def _get_hotel_category(stars: int, rating: float) -> str:
    """Determine hotel category"""
    if stars >= 5 or rating >= 9.0:
        return "luxury"
    elif stars >= 4 or rating >= 8.0:
        return "upscale"
    elif stars >= 3:
        return "midscale"
    else:
        return "budget"


def _calculate_scores(hotel_data: Dict, room_data: Optional[Dict], preferences: List[int]) -> common_pb2.ComponentScores:
    """Calculate normalized component scores"""
    # Price score (inverse - lower price = higher score)
    # Assuming price range 50-500 USD
    price = hotel_data.get("price_per_night", 200)
    price_score = max(0, min(1, 1 - (price - 50) / 450))
    
    # Quality score from rating
    rating = hotel_data.get("rating", 0)
    quality_score = rating / 10.0 if rating else 0.5
    
    # Convenience score (distance to center)
    distance = hotel_data.get("distance_to_center_km", 5)
    convenience_score = max(0, min(1, 1 - distance / 10))
    
    # Preference score based on matching preferences
    preference_score = 0.5  # Default neutral score
    if common_pb2.LUXURY in preferences and hotel_data.get("stars", 0) >= 4:
        preference_score += 0.3
    if common_pb2.BUDGET in preferences and hotel_data.get("stars", 0) <= 3:
        preference_score += 0.3
    preference_score = min(1.0, preference_score)
    
    scores = common_pb2.ComponentScores()
    scores.price_score = price_score
    scores.quality_score = quality_score
    scores.convenience_score = convenience_score
    scores.preference_score = preference_score
    
    return scores


def _transform_room_data(room_raw: Dict) -> hotel_pb2.RoomInfo:
    """Transform raw room data to RoomInfo protobuf"""
    room_info = hotel_pb2.RoomInfo()
    
    # Extract features from amenities
    amenities = room_raw.get("roomAmenities", [])
    for amenity in amenities[:10]:  # Limit features
        room_info.features.append(amenity.get("name", ""))
    
    # Parse bed information
    bed_types = room_raw.get("bedTypes", [])
    room_info.type = room_raw.get("roomName", "Standard Room")
    room_info.beds = len(bed_types) if bed_types else 1
    room_info.bed_type = bed_types[0] if bed_types else "standard"
    room_info.max_occupancy = room_raw.get("maxOccupancy", 2)
    room_info.size_sqm = float(room_raw.get("roomSizeSquare", 0))
    
    return room_info


def transform_hotel_data(
    hotel_raw: Dict, 
    room_raw: Optional[Dict], 
    start_date: str,
    end_date: str,
    preferences: List[int],
    provider: str
) -> hotel_pb2.HotelOption:
    """Transform raw API data to HotelOption protobuf"""
    
    hotel_option = hotel_pb2.HotelOption()
    
    # Basic info
    hotel_option.id = hotel_raw.get("id", "")
    hotel_option.name = hotel_raw.get("name", "")
    hotel_option.description = hotel_raw.get("hotelDescription", "")[:500]  # Truncate
    
    # Location
    hotel_option.location.city = hotel_raw.get("city", "")
    hotel_option.location.country = hotel_raw.get("country", "")
    hotel_option.location.latitude = hotel_raw.get("latitude", 0.0)
    hotel_option.location.longitude = hotel_raw.get("longitude", 0.0)
    
    # Distance (mock - in real implementation calculate from coordinates)
    hotel_option.distance_to_center_km = 2.5
    
    # Rating
    hotel_option.rating = hotel_raw.get("rating", 0.0)
    hotel_option.review_count = hotel_raw.get("reviewCount", 0)
    hotel_option.rating_category = _get_rating_category(hotel_raw.get("rating", 0))
    
    # Calculate nights
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    nights = (end - start).days
    
    # Pricing (mock - in real implementation, get from pricing API or response)
    base_price = 150.0
    currency = hotel_raw.get("currency", "USD")
    
    hotel_option.price_per_night.currency = currency
    hotel_option.price_per_night.amount = base_price
    
    hotel_option.total_price.currency = currency
    hotel_option.total_price.amount = base_price * nights
    
    # Room data if available
    if room_raw:
        hotel_option.room.CopyFrom(_transform_room_data(room_raw))
    
    # Amenities (simplified - in real impl, map facility IDs to names)
    for fid in hotel_raw.get("facilityIds", [])[:10]:
        hotel_option.amenities.append(f"Amenity_{fid}")
    
    # Category and stars
    hotel_option.category = _get_hotel_category(
        hotel_raw.get("stars", 0), 
        hotel_raw.get("rating", 0)
    )
    hotel_option.star_rating = hotel_raw.get("stars", 0)
    
    # Scores
    hotel_data_for_scoring = {
        "price_per_night": base_price,
        "rating": hotel_raw.get("rating", 0),
        "distance_to_center_km": 2.5,
        "stars": hotel_raw.get("stars", 3)
    }
    hotel_option.scores.CopyFrom(_calculate_scores(hotel_data_for_scoring, room_raw, preferences))
    
    # Booking info - use provider from parameter, not hardcoded
    hotel_option.booking_url = f"https://booking.example.com/hotels/{hotel_raw.get('id')}"
    hotel_option.provider = provider
    hotel_option.available = True
    
    return hotel_option
