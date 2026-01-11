from typing import List, Optional, Union
from enum import IntEnum, Enum
from pydantic import BaseModel, Field

# ==========================================
# COMMON
# ==========================================

class PreferenceType(IntEnum):
    PREFERENCE_UNKNOWN = 0
    LUXURY = 1
    BUDGET = 2
    ROMANTIC = 3
    FAMILY = 4
    ADVENTURE = 5
    CULTURE = 6
    FOOD = 7
    NATURE = 8
    BEACH = 9
    CITY = 10

class Money(BaseModel):
    currency: str = "USD"
    amount: float = 0.0

class Location(BaseModel):
    city: str = ""
    country: str = ""
    airport_code: str = ""  # IATA code (optional)
    latitude: float = 0.0
    longitude: float = 0.0

class DateRange(BaseModel):
    start_date: str = ""  # ISO 8601 format: YYYY-MM-DD
    end_date: str = ""

class TimeRange(BaseModel):
    start_time: str = ""  # ISO 8601 format: HH:MM
    end_time: str = ""

class ComponentScores(BaseModel):
    price_score: float = 0.0      # Lower price = higher score
    quality_score: float = 0.0    # Rating, comfort, etc.
    convenience_score: float = 0.0 # Duration, location, etc.
    preference_score: float = 0.0  # Match to user preferences

class SearchMetadata(BaseModel):
    total_results: int = 0
    search_id: str = ""
    timestamp: str = ""
    data_source: str = ""

# ==========================================
# HOTEL
# ==========================================

class RoomInfo(BaseModel):
    type: str = ""  # standard, deluxe, suite, etc.
    beds: int = 0
    bed_type: str = ""  # king, queen, twin, etc.
    max_occupancy: int = 0
    size_sqm: float = 0.0
    features: List[str] = Field(default_factory=list)

class Fee(BaseModel):
    name: str = ""  # resort fee, parking, etc.
    amount: Money = Field(default_factory=Money)
    mandatory: bool = False

class HotelOption(BaseModel):
    id: str = ""
    
    # Basic info
    name: str = ""
    description: str = ""
    location: Location = Field(default_factory=Location)
    distance_to_center_km: float = 0.0
    
    # Rating
    rating: float = 0.0  # 0-5 scale
    review_count: int = 0
    rating_category: str = ""  # e.g., "Excellent", "Very Good"
    
    # Pricing
    price_per_night: Money = Field(default_factory=Money)
    total_price: Money = Field(default_factory=Money)
    additional_fees: List[Fee] = Field(default_factory=list)
    
    # Room details
    room: RoomInfo = Field(default_factory=RoomInfo)
    
    # Hotel features
    amenities: List[str] = Field(default_factory=list)
    category: str = ""  # budget, midscale, upscale, luxury
    star_rating: int = 0  # 1-5 stars
    
    # Scores
    scores: ComponentScores = Field(default_factory=ComponentScores)
    
    # Booking
    booking_url: str = ""
    provider: str = ""
    available: bool = False

class HotelSearchRequest(BaseModel):
    location: Location = Field(default_factory=Location)
    dates: DateRange = Field(default_factory=DateRange)
    guests: int = 0
    rooms: int = 0
    preferences: List[PreferenceType] = Field(default_factory=list)
    
    # Filters
    max_results: int = 0
    max_price_per_night: float = 0.0
    min_rating: float = 0.0  # 0-5 scale
    amenities: List[int] = Field(default_factory=list)

class HotelSearchResponse(BaseModel):
    options: List[HotelOption] = Field(default_factory=list)
    metadata: SearchMetadata = Field(default_factory=SearchMetadata)


# ==========================================
# FLIGHT
# ==========================================

class AmenityInfo(BaseModel):
    wifi: bool = False
    meal: bool = False
    entertainment: bool = False
    power_outlet: bool = False
    legroom_inches: int = 0

class Layover(BaseModel):
    airport: Location = Field(default_factory=Location)
    duration_minutes: int = 0

class FlightSegment(BaseModel):
    origin: Location = Field(default_factory=Location)
    destination: Location = Field(default_factory=Location)
    
    departure_time: str = ""  # ISO 8601: YYYY-MM-DDTHH:MM:SS
    arrival_time: str = ""
    
    duration_minutes: int = 0
    stops: int = 0
    layovers: List[Layover] = Field(default_factory=list)
    
    airline: str = ""
    flight_number: str = ""
    aircraft: str = ""
    cabin_class: str = ""
    
    amenities: AmenityInfo = Field(default_factory=AmenityInfo)

class FlightOption(BaseModel):
    id: str = ""  # Unique identifier for caching
    
    # Outbound flight
    outbound: FlightSegment = Field(default_factory=FlightSegment)
    
    # Return flight (if round-trip)
    return_flight: FlightSegment = Field(default_factory=FlightSegment, alias="return") # 'return' is a keyword
    
    # Pricing
    total_price: Money = Field(default_factory=Money)
    price_per_person: Money = Field(default_factory=Money)
    
    # Scores
    scores: ComponentScores = Field(default_factory=ComponentScores)
    
    # Booking info
    booking_url: str = ""
    provider: str = ""  # airline or booking platform
    available: bool = False

    class Config:
        populate_by_name = True

class FlightSearchRequest(BaseModel):
    origin: Location = Field(default_factory=Location)
    destination: Location = Field(default_factory=Location)
    departure_date: str = ""  # ISO 8601: YYYY-MM-DD
    return_date: str = ""     # Optional for one-way
    passengers: int = 0
    cabin_class: str = ""     # economy, premium_economy, business, first
    preferences: List[PreferenceType] = Field(default_factory=list)
    
    # Search constraints
    max_results: int = 20      # Default: 20
    max_price: float = 0.0       # Optional price filter
    max_stops: int = 0       # 0=direct, 1=one stop, etc.

class FlightSearchResponse(BaseModel):
    options: List[FlightOption] = Field(default_factory=list)
    metadata: SearchMetadata = Field(default_factory=SearchMetadata)


# ==========================================
# ACTIVITY
# ==========================================

class ActivityCategory(IntEnum):
    CATEGORY_UNKNOWN = 0
    TOUR = 1
    MUSEUM = 2
    RESTAURANT = 3
    SHOW = 4
    OUTDOOR = 5
    WATER_SPORTS = 6
    NIGHTLIFE = 7
    SHOPPING = 8
    SPA = 9
    ADVENTURE = 10
    CULTURAL = 11
    FOOD_TOUR = 12

class PriceDetails(BaseModel):
    adult_price: Money = Field(default_factory=Money)
    child_price: Money = Field(default_factory=Money)
    senior_price: Money = Field(default_factory=Money)

class TimeSlot(BaseModel):
    date: str = ""  # ISO 8601: YYYY-MM-DD
    time: str = ""  # ISO 8601: HH:MM
    available_spots: int = 0

class ActivityOption(BaseModel):
    id: str = ""
    
    # Basic info
    name: str = ""
    description: str = ""
    category: ActivityCategory = ActivityCategory.CATEGORY_UNKNOWN
    location: Location = Field(default_factory=Location)
    distance_from_query_km: float = 0.0
    
    # Rating
    rating: float = 0.0  # 0-5 scale
    review_count: int = 0
    
    # Pricing
    price_per_person: Money = Field(default_factory=Money)
    price_details: PriceDetails = Field(default_factory=PriceDetails)
    
    # Timing
    duration_minutes: int = 0
    available_times: List[TimeSlot] = Field(default_factory=list)
    
    # Details
    highlights: List[str] = Field(default_factory=list)
    included: List[str] = Field(default_factory=list)
    excluded: List[str] = Field(default_factory=list)
    min_participants: int = 0
    max_participants: int = 0
    difficulty_level: str = ""  # easy, moderate, challenging
    
    # Logistics
    hotel_pickup: bool = False
    meal_included: bool = False
    cancellation_policy: str = ""
    
    # Scores
    scores: ComponentScores = Field(default_factory=ComponentScores)
    
    # Booking
    booking_url: str = ""
    provider: str = ""
    available: bool = False
    
    # Images
    image_urls: List[str] = Field(default_factory=list)

class ActivitySearchRequest(BaseModel):
    location: Location = Field(default_factory=Location)
    dates: DateRange = Field(default_factory=DateRange)
    preferences: List[PreferenceType] = Field(default_factory=list)
    categories: List[ActivityCategory] = Field(default_factory=list)
    
    # Filters
    max_results: int = 0
    max_price: float = 0.0
    min_rating: float = 0.0
    max_distance_km: int = 0  # from location center
    preferred_time: TimeRange = Field(default_factory=TimeRange)

class ActivitySearchResponse(BaseModel):
    options: List[ActivityOption] = Field(default_factory=list)
    metadata: SearchMetadata = Field(default_factory=SearchMetadata)


# ==========================================
# TRANSPORT
# ==========================================

class TransportMode(IntEnum):
    MODE_UNKNOWN = 0
    RENTAL_CAR = 1
    TAXI = 2
    RIDESHARE = 3
    TRAIN = 4
    BUS = 5
    FERRY = 6
    PRIVATE_TRANSFER = 7
    PUBLIC_TRANSIT = 8

class RentalCarDetails(BaseModel):
    vehicle_class: str = ""  # economy, compact, suv, etc.
    vehicle_model: str = ""
    seats: int = 0
    luggage: int = 0
    transmission: str = ""  # automatic, manual
    air_conditioning: bool = False
    unlimited_mileage: bool = False
    included_features: List[str] = Field(default_factory=list)
    daily_rate: Money = Field(default_factory=Money)
    insurance_cost: Money = Field(default_factory=Money)

class RideDetails(BaseModel):
    vehicle_type: str = ""  # sedan, suv, van, etc.
    seats: int = 0
    shared: bool = False
    estimated_wait_minutes: int = 0

class PublicTransitDetails(BaseModel):
    line: str = ""  # train line, bus number, etc.
    stops: int = 0
    transfer_points: List[str] = Field(default_factory=list)
    service_class: str = ""  # standard, first class, etc.
    wifi: bool = False
    food_service: bool = False

class TransportDetails(BaseModel):
    # Mimicking oneof from proto using optional fields
    rental_car: Optional[RentalCarDetails] = None
    ride: Optional[RideDetails] = None
    transit: Optional[PublicTransitDetails] = None

class TransportOption(BaseModel):
    id: str = ""
    
    mode: TransportMode = TransportMode.MODE_UNKNOWN
    provider: str = ""  # Uber, Hertz, Amtrak, etc.
    
    # Route
    origin: Location = Field(default_factory=Location)
    destination: Location = Field(default_factory=Location)
    distance_km: float = 0.0
    
    # Timing
    departure_time: str = ""  # ISO 8601
    arrival_time: str = ""
    duration_minutes: int = 0
    
    # Pricing
    total_price: Money = Field(default_factory=Money)
    price_per_person: Money = Field(default_factory=Money)
    
    # Details
    details: TransportDetails = Field(default_factory=TransportDetails)
    
    # Scores
    scores: ComponentScores = Field(default_factory=ComponentScores)
    
    # Booking
    booking_url: str = ""
    available: bool = False

class TransportSearchRequest(BaseModel):
    origin: Location = Field(default_factory=Location)
    destination: Location = Field(default_factory=Location)
    date: str = ""  # ISO 8601: YYYY-MM-DD
    time: str = ""  # ISO 8601: HH:MM (optional)
    passengers: int = 0
    preferred_modes: List[TransportMode] = Field(default_factory=list)
    
    # Filters
    max_results: int = 0
    max_price: float = 0.0
    max_duration_minutes: int = 0

class TransportSearchResponse(BaseModel):
    options: List[TransportOption] = Field(default_factory=list)
    metadata: SearchMetadata = Field(default_factory=SearchMetadata)

class SectionType(str, Enum):
    TRANSFER = "transfer"
    FLIGHT = "flight"
    STAY = "stay"

class TransferRequest(TransportSearchRequest):
    pass

class FlightRequest(FlightSearchRequest):
    pass

class StayRequest(BaseModel):
    hotel_request: HotelSearchRequest = Field(default_factory=HotelSearchRequest)
    activity_request: ActivitySearchRequest = Field(default_factory=ActivitySearchRequest)

class TripSection(BaseModel):
    type: SectionType
    data: Union[TransferRequest, FlightRequest, StayRequest]

class TripRequest(BaseModel):
    sections: List[TripSection] = Field(default_factory=list)

class TransferResponse(BaseModel):
    options: List[TransportOption] = Field(default_factory=list)

class FlightResponse(BaseModel):
    options: List[FlightOption] = Field(default_factory=list)

class StayResponse(BaseModel):
    hotel_options: List[HotelOption] = Field(default_factory=list)
    activity_options: List[ActivityOption] = Field(default_factory=list)

class TripSectionResponse(BaseModel):
    type: SectionType
    data: Union[TransferResponse, FlightResponse, StayResponse]

class TripResponse(BaseModel):
    sections: List[TripSectionResponse] = Field(default_factory=list)


class FinalStayOption(BaseModel):
    hotel: HotelOption = Field(default_factory=HotelOption)
    activity: List[ActivityOption] = Field(default_factory=list)

class FinalTripSection(BaseModel):
    type: SectionType
    data: Union[TransportOption, FlightOption, FinalStayOption]

class FinalTripLayout(BaseModel):
    sections: List[FinalTripSection] = Field(default_factory=list)