from typing import Dict, List, Optional
from datetime import datetime
from shared.data_types import hotel_pb2, common_pb2


def get_rating_category(rating: float) -> str:
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


def get_hotel_category(stars: int, rating: float) -> str:
    """Determine hotel category"""
    if stars >= 5 or rating >= 9.0:
        return "luxury"
    elif stars >= 4 or rating >= 8.0:
        return "upscale"
    elif stars >= 3:
        return "midscale"
    else:
        return "budget"


def calculate_scores(
    price: float,
    rating: float,
    distance: float,
    stars: int,
    preferences: List[int]
) -> common_pb2.ComponentScores:
    """Calculate normalized component scores"""
    scores = common_pb2.ComponentScores()
    
    # Price score (inverse - lower price = higher score)
    # Assuming price range 50-500 USD per night
    scores.price_score = max(0, min(1, 1 - (price - 50) / 450))
    
    # Quality score from rating (0-10 scale to 0-1)
    scores.quality_score = rating / 10.0 if rating else 0.5
    
    # Convenience score (distance to center in km)
    scores.convenience_score = max(0, min(1, 1 - distance / 10))
    
    # Preference score based on matching preferences
    preference_score = 0.5  # Default neutral score
    if common_pb2.LUXURY in preferences and stars >= 4:
        preference_score += 0.3
    if common_pb2.BUDGET in preferences and stars <= 3:
        preference_score += 0.3
    scores.preference_score = min(1.0, preference_score)
    
    return scores


def transform_room_data(room_raw: Optional[Dict]) -> Optional[hotel_pb2.RoomInfo]:
    """Transform raw room data to RoomInfo protobuf"""
    if not room_raw:
        return None
    
    room_info = hotel_pb2.RoomInfo()
    
    # Extract features from amenities
    amenities = room_raw.get("roomAmenities", [])
    for amenity in amenities[:10]:  # Limit features
        if isinstance(amenity, dict):
            room_info.features.append(amenity.get("name", ""))
        else:
            room_info.features.append(str(amenity))
    
    # Room details
    room_info.type = room_raw.get("roomName", "Standard Room")
    room_info.beds = 1  # Default
    room_info.bed_type = "standard"
    room_info.max_occupancy = room_raw.get("maxOccupancy", 2)
    room_info.size_sqm = float(room_raw.get("roomSizeSquare", 0))
    
    return room_info


def transform_fees(taxes_and_fees: List[Dict], currency: str) -> List[hotel_pb2.Fee]:
    """Transform taxes and fees to Fee protobuf list"""
    fees = []
    
    for tax_fee in taxes_and_fees:
        if not tax_fee.get("included", True):  # Only add non-included fees
            fee = hotel_pb2.Fee()
            fee.name = tax_fee.get("description", "Additional Fee")
            fee.amount.currency = currency
            fee.amount.amount = tax_fee.get("amount", 0.0)
            fee.mandatory = True
            fees.append(fee)
    
    return fees


def transform_hotel_data(
    hotel_raw: Dict,
    room_raw: Optional[Dict],
    start_date: str,
    end_date: str,
    preferences: List[int],
    provider: str,
    rate_info: Optional[Dict] = None
) -> hotel_pb2.HotelOption:
    """
    Transform raw API data to HotelOption protobuf
    
    Args:
        hotel_raw: Raw hotel data from get_hotels API
        room_raw: Raw room data
        start_date: Check-in date (YYYY-MM-DD)
        end_date: Check-out date (YYYY-MM-DD)
        preferences: List of preference enums
        provider: Provider name
        rate_info: Rate information from availability check (optional)
    """
    hotel_option = hotel_pb2.HotelOption()
    
    # Basic info
    hotel_option.id = hotel_raw.get("id", "")
    hotel_option.name = hotel_raw.get("name", "")
    
    # Clean and truncate description
    description = hotel_raw.get("hotelDescription", "")
    # Remove HTML tags if present
    import re
    description = re.sub('<[^<]+?>', '', description)
    hotel_option.description = description[:500]  # Truncate
    
    # Location
    hotel_option.location.city = hotel_raw.get("city", "")
    hotel_option.location.country = hotel_raw.get("country", "")
    hotel_option.location.latitude = hotel_raw.get("latitude", 0.0)
    hotel_option.location.longitude = hotel_raw.get("longitude", 0.0)
    
    # Distance to center (mock - in real implementation calculate from coordinates)
    hotel_option.distance_to_center_km = 2.5
    
    # Rating
    hotel_option.rating = hotel_raw.get("rating", 0.0)
    hotel_option.review_count = hotel_raw.get("reviewCount", 0)
    hotel_option.rating_category = get_rating_category(hotel_raw.get("rating", 0))
    
    # Calculate nights
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    nights = (end - start).days
    
    # Pricing - use rate_info if available, otherwise use defaults
    currency = hotel_raw.get("currency", "USD")
    
    if rate_info and "price" in rate_info:
        # Use actual rate data from availability check
        price_data = rate_info["price"]
        total_amount = price_data.get("amount", 0.0)
        price_per_night = total_amount / nights if nights > 0 else total_amount
        
        hotel_option.price_per_night.currency = price_data.get("currency", currency)
        hotel_option.price_per_night.amount = price_per_night
        
        hotel_option.total_price.currency = price_data.get("currency", currency)
        hotel_option.total_price.amount = total_amount
        
        # Add fees from rate info
        taxes_and_fees = rate_info.get("taxes_and_fees", [])
        fees = transform_fees(taxes_and_fees, price_data.get("currency", currency))
        hotel_option.additional_fees.extend(fees)
        
        # Set availability
        hotel_option.available = rate_info.get("available", True)
        
        # Use actual supplier
        if "supplier" in rate_info:
            provider = rate_info["supplier"]
    else:
        # Use mock pricing if no rate info
        base_price = 150.0
        hotel_option.price_per_night.currency = currency
        hotel_option.price_per_night.amount = base_price
        
        hotel_option.total_price.currency = currency
        hotel_option.total_price.amount = base_price * nights
        
        hotel_option.available = False  # Mark as unavailable if no rate info
    
    # Room data if available
    if room_raw:
        room_info = transform_room_data(room_raw)
        if room_info:
            hotel_option.room.CopyFrom(room_info)
    
    # Amenities (map facility IDs to simple labels)
    facility_ids = hotel_raw.get("facilityIds", [])
    for fid in facility_ids[:10]:  # Limit to 10
        hotel_option.amenities.append(f"Facility_{fid}")
    
    # Category and stars
    stars = hotel_raw.get("stars", 0)
    hotel_option.category = get_hotel_category(stars, hotel_raw.get("rating", 0))
    hotel_option.star_rating = stars
    
    # Calculate scores
    price_for_scoring = hotel_option.price_per_night.amount
    scores = calculate_scores(
        price=price_for_scoring,
        rating=hotel_raw.get("rating", 0),
        distance=hotel_option.distance_to_center_km,
        stars=stars,
        preferences=preferences
    )
    hotel_option.scores.CopyFrom(scores)
    
    # Booking info
    hotel_option.booking_url = f"https://booking.liteapi.travel/hotels/{hotel_raw.get('id')}"
    hotel_option.provider = provider
    
    return hotel_option