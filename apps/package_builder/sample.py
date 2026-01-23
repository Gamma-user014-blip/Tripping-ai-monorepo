# sample.py
# Large sample data for testing the package builder

from typing import List
from enums_and_models import (
    PreferenceType,
    Money,
    Location,
    ComponentScores,
    RoomInfo,
    Fee,
    HotelOption,
    FlightSegment,
    FlightOption,
    ActivityCategory,
    PriceDetails,
    TimeRange,
    TimeSlot,
    ActivityOption,
)

# ======================
# FLIGHTS
# ======================

flights_packet = [
    {
        "id": "f1",
        "outbound": {
            "origin": {
                "city": "New York",
                "country": "USA",
                "airport_code": "JFK",
                "latitude": 40.6413,
                "longitude": -73.7781,
            },
            "destination": {
                "city": "London",
                "country": "UK",
                "airport_code": "LHR",
                "latitude": 51.4700,
                "longitude": -0.4543,
            },
            "departure_time": "2026-06-01T10:00:00",
            "arrival_time": "2026-06-01T18:00:00",
            "duration_minutes": 480,
            "stops": 0,
            "layovers": [],
            "airline": "British Airways",
            "flight_number": "BA178",
            "aircraft": "Boeing 777-300ER",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": True,
                "entertainment": True,
                "power_outlet": True,
                "legroom_inches": 31,
            },
            "luggage": {
                "checked_bags": 1,
                "checked_bag_weight_kg": 23.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 8.0,
                "carry_on_dimensions_cm": "55x40x23",
            },
        },
        "total_price": {"currency": "USD", "amount": 1600.0},  # 2 passengers example
        "price_per_person": {"currency": "USD", "amount": 800.0},
        "scores": {
            "price_score": 7.5,
            "quality_score": 9.0,
            "convenience_score": 9.5,
            "preference_score": 8.5,
        },
        "booking_url": "https://example.com/book/BA178",
        "provider": "British Airways",
        "available": True,
    },
    {
        "id": "f2",
        "outbound": {
            "origin": {
                "city": "New York",
                "country": "USA",
                "airport_code": "JFK",
                "latitude": 40.6413,
                "longitude": -73.7781,
            },
            "destination": {
                "city": "London",
                "country": "UK",
                "airport_code": "LHR",
                "latitude": 51.4700,
                "longitude": -0.4543,
            },
            "departure_time": "2026-06-01T12:00:00",
            "arrival_time": "2026-06-02T02:00:00",
            "duration_minutes": 840,
            "stops": 1,
            "layovers": [
                {
                    "airport": {
                        "city": "Frankfurt",
                        "country": "Germany",
                        "airport_code": "FRA",
                        "latitude": 50.0379,
                        "longitude": 8.5622,
                    },
                    "start_time": "2026-06-01T22:00:00",
                    "end_time": "2026-06-02T00:00:00",
                    "duration_minutes": 120,
                    "arrival_terminal": "1",
                    "departure_terminal": "1",
                    "airline_before": "Lufthansa",
                    "airline_after": "Lufthansa",
                    "is_airline_change": False,
                    "is_terminal_change": False,
                    "overnight": False,
                }
            ],
            "airline": "Lufthansa",
            "flight_number": "LH401",
            "aircraft": "Airbus A350-900",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": True,
                "entertainment": True,
                "power_outlet": True,
                "legroom_inches": 30,
            },
            "luggage": {
                "checked_bags": 1,
                "checked_bag_weight_kg": 23.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 8.0,
                "carry_on_dimensions_cm": "55x40x23",
            },
        },
        "total_price": {"currency": "USD", "amount": 1200.0},
        "price_per_person": {"currency": "USD", "amount": 600.0},
        "scores": {
            "price_score": 8.5,
            "quality_score": 8.0,
            "convenience_score": 7.0,
            "preference_score": 7.5,
        },
        "booking_url": "https://example.com/book/LH401",
        "provider": "Lufthansa",
        "available": True,
    },
]


# More flights for stage 4
flights_packet2 = [
    {
        "id": "f5",
        "outbound": {
            "origin": {
                "city": "Manchester",
                "country": "UK",
                "airport_code": "MAN",
                "latitude": 53.3650,
                "longitude": -2.2727,
            },
            "destination": {
                "city": "New York",
                "country": "USA",
                "airport_code": "JFK",
                "latitude": 40.6413,
                "longitude": -73.7781,
            },
            "departure_time": "2026-06-15T10:00:00",
            "arrival_time": "2026-06-15T18:00:00",
            "duration_minutes": 480,
            "stops": 0,
            "layovers": [],
            "airline": "Virgin Atlantic",
            "flight_number": "VS75",
            "aircraft": "Airbus A330-300",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": True,
                "entertainment": True,
                "power_outlet": True,
                "legroom_inches": 31,
            },
            "luggage": {
                "checked_bags": 1,
                "checked_bag_weight_kg": 23.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 8.0,
                "carry_on_dimensions_cm": "55x40x23",
            },
        },
        "total_price": {"currency": "USD", "amount": 900.0},
        "price_per_person": {"currency": "USD", "amount": 900.0},
        "scores": {
            "price_score": 7.0,
            "quality_score": 8.5,
            "convenience_score": 9.0,
            "preference_score": 8.0,
        },
        "booking_url": "https://example.com/book/VS75",
        "provider": "Virgin Atlantic",
        "available": True,
    },
    {
        "id": "f6",
        "outbound": {
            "origin": {
                "city": "Manchester",
                "country": "UK",
                "airport_code": "MAN",
                "latitude": 53.3650,
                "longitude": -2.2727,
            },
            "destination": {
                "city": "New York",
                "country": "USA",
                "airport_code": "JFK",
                "latitude": 40.6413,
                "longitude": -73.7781,
            },
            "departure_time": "2026-06-15T12:00:00",
            "arrival_time": "2026-06-16T02:00:00",
            "duration_minutes": 840,
            "stops": 1,
            "layovers": [
                {
                    "airport": {
                        "city": "Paris",
                        "country": "France",
                        "airport_code": "CDG",
                        "latitude": 49.0097,
                        "longitude": 2.5479,
                    },
                    "start_time": "2026-06-15T20:00:00",
                    "end_time": "2026-06-15T22:00:00",
                    "duration_minutes": 120,
                    "arrival_terminal": "2E",
                    "departure_terminal": "2E",
                    "airline_before": "Air France",
                    "airline_after": "Air France",
                    "is_airline_change": False,
                    "is_terminal_change": False,
                    "overnight": False,
                }
            ],
            "airline": "Air France",
            "flight_number": "AF123",
            "aircraft": "Boeing 787-9",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": True,
                "entertainment": True,
                "power_outlet": True,
                "legroom_inches": 30,
            },
            "luggage": {
                "checked_bags": 1,
                "checked_bag_weight_kg": 23.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 8.0,
                "carry_on_dimensions_cm": "55x40x23",
            },
        },
        "total_price": {"currency": "USD", "amount": 650.0},
        "price_per_person": {"currency": "USD", "amount": 650.0},
        "scores": {
            "price_score": 8.5,
            "quality_score": 8.0,
            "convenience_score": 7.0,
            "preference_score": 7.5,
        },
        "booking_url": "https://example.com/book/AF123",
        "provider": "Air France",
        "available": True,
    },
]


def get_flights():
    return flights_packet


def get_flights2():
    return flights_packet2


# ======================
# HOTELS
# ======================

hotels_packet = {
    "options": [
        {
            "id": "h1",
            "name": "The Savoy",
            "description": "Iconic luxury hotel on the Strand with river-view rooms and fine dining.",
            "location": {
                "city": "London",
                "country": "UK",
                "latitude": 51.5100,
                "longitude": -0.1200,
            },
            "distance_to_center_km": 0.5,
            "image": "https://example.com/images/savoy.jpg",
            "rating": 5.0,
            "review_count": 4200,
            "rating_category": "Excellent",
            "price_per_night": {"currency": "GBP", "amount": 500.0},
            "total_price": {"currency": "GBP", "amount": 1500.0},  # 3 nights
            "additional_fees": [
                {
                    "name": "Resort fee",
                    "amount": {"currency": "GBP", "amount": 20.0},
                    "mandatory": True,
                }
            ],
            "room": {
                "type": "suite",
                "beds": 1,
                "bed_type": "king",
                "max_occupancy": 2,
                "size_sqm": 45.0,
                "features": ["city view", "river view", "espresso machine"],
            },
            "amenities": ["wifi", "pool", "gym", "spa", "restaurant", "bar"],
            "category": "luxury",
            "star_rating": 5,
            "scores": {
                "price_score": 6.5,
                "quality_score": 9.5,
                "convenience_score": 9.0,
                "preference_score": 9.0,
            },
            "booking_url": "https://example.com/book/savoy_london",
            "provider": "HotelDirect",
            "available": True,
        },
        {
            "id": "h2",
            "name": "Ibis London",
            "description": "Modern budget hotel with compact rooms and easy access to public transport.",
            "location": {
                "city": "London",
                "country": "UK",
                "latitude": 51.5150,
                "longitude": -0.1300,
            },
            "distance_to_center_km": 1.2,
            "image": "https://example.com/images/ibis_london.jpg",
            "rating": 3.0,
            "review_count": 2100,
            "rating_category": "Good",
            "price_per_night": {"currency": "GBP", "amount": 100.0},
            "total_price": {"currency": "GBP", "amount": 300.0},
            "additional_fees": [],
            "room": {
                "type": "standard",
                "beds": 1,
                "bed_type": "queen",
                "max_occupancy": 2,
                "size_sqm": 18.0,
                "features": ["desk", "air conditioning"],
            },
            "amenities": ["wifi", "breakfast"],
            "category": "budget",
            "star_rating": 3,
            "scores": {
                "price_score": 9.0,
                "quality_score": 7.0,
                "convenience_score": 8.0,
                "preference_score": 7.5,
            },
            "booking_url": "https://example.com/book/ibis_london",
            "provider": "HotelDirect",
            "available": True,
        },
        {
            "id": "kensington_suite",
            "name": "Kensington Suite",
            "description": "Serviced apartments with kitchenettes in a quiet Kensington street.",
            "location": {
                "city": "London",
                "country": "UK",
                "latitude": 51.5000,
                "longitude": -0.2000,
            },
            "distance_to_center_km": 3.5,
            "image": "https://example.com/images/kensington_suite.jpg",
            "rating": 4.5,
            "review_count": 980,
            "rating_category": "Very Good",
            "price_per_night": {"currency": "USD", "amount": 250.0},
            "total_price": {"currency": "USD", "amount": 750.0},
            "additional_fees": [
                {
                    "name": "Cleaning fee",
                    "amount": {"currency": "USD", "amount": 40.0},
                    "mandatory": True,
                }
            ],
            "room": {
                "type": "apartment",
                "beds": 1,
                "bed_type": "queen",
                "max_occupancy": 3,
                "size_sqm": 35.0,
                "features": ["kitchen", "sofa bed"],
            },
            "amenities": ["wifi", "kitchen", "laundry"],
            "category": "midscale",
            "star_rating": 4,
            "scores": {
                "price_score": 8.0,
                "quality_score": 8.5,
                "convenience_score": 7.5,
                "preference_score": 8.0,
            },
            "booking_url": "https://example.com/book/kensington_suite",
            "provider": "ApartStay",
            "available": True,
        },
    ]
}

hotels_packet2 = {
    "options": [
        {
            "id": "manchester_central_hotel",
            "name": "Manchester Central Hotel",
            "description": "Comfortable city-center hotel near Piccadilly Gardens.",
            "location": {
                "city": "Manchester",
                "country": "UK",
                "latitude": 53.4808,
                "longitude": -2.2426,
            },
            "distance_to_center_km": 0.4,
            "image": "https://example.com/images/manchester_central_hotel.jpg",
            "rating": 4.0,
            "review_count": 1350,
            "rating_category": "Very Good",
            "price_per_night": {"currency": "USD", "amount": 180.0},
            "total_price": {"currency": "USD", "amount": 540.0},
            "additional_fees": [],
            "room": {
                "type": "standard",
                "beds": 1,
                "bed_type": "queen",
                "max_occupancy": 2,
                "size_sqm": 22.0,
                "features": ["city view", "desk"],
            },
            "amenities": ["wifi", "parking", "restaurant"],
            "category": "midscale",
            "star_rating": 4,
            "scores": {
                "price_score": 8.0,
                "quality_score": 8.0,
                "convenience_score": 8.5,
                "preference_score": 8.0,
            },
            "booking_url": "https://example.com/book/manchester_central_hotel",
            "provider": "HotelDirect",
            "available": True,
        }
    ]
}


# ======================
# ACTIVITIES
# ======================

activities_packet = {
    "options": [
        # London Activities
        {
            "id": "a1",
            "name": "London Eye Experience",
            "description": "Enjoy panoramic views of London from the iconic London Eye.",
            "category": ActivityCategory.TOUR,
            "location": {
                "city": "London",
                "country": "UK",
                "latitude": 51.5033,
                "longitude": -0.1196,
            },
            "distance_from_query_km": 2.0,
            "rating": 4.7,
            "review_count": 3500,
            "price_per_person": {"currency": "GBP", "amount": 35.0},
            "price_details": {
                "adult_price": {"currency": "GBP", "amount": 35.0},
                "child_price": {"currency": "GBP", "amount": 25.0},
                "senior_price": {"currency": "GBP", "amount": 30.0},
            },
            "duration_minutes": 60,
            "available_times": [
                {"date": "2026-06-02", "time": "10:00", "available_spots": 10},
                {"date": "2026-06-02", "time": "12:00", "available_spots": 10},
            ],
            "highlights": ["360-degree views", "River Thames"],
            "included": ["Entrance ticket", "Guided information"],
            "excluded": ["Transport", "Food"],
            "min_participants": 1,
            "max_participants": 30,
            "difficulty_level": "easy",
            "hotel_pickup": True,
            "meal_included": False,
            "cancellation_policy": "24 hours before",
            "scores": {
                "price_score": 8.0,
                "quality_score": 9.5,
                "convenience_score": 9.0,
                "preference_score": 9.0,
            },
            "booking_url": "https://example.com/book/london_eye",
            "provider": "London Tours",
            "available": True,
            "image_urls": ["https://example.com/images/london_eye.jpg"],
        },
        {
            "id": "a2",
            "name": "British Museum Tour",
            "description": "Explore one of the world's oldest and largest museums with a guided tour.",
            "category": ActivityCategory.MUSEUM,
            "location": {
                "city": "London",
                "country": "UK",
                "latitude": 51.5194,
                "longitude": -0.1270,
            },
            "distance_from_query_km": 1.5,
            "rating": 4.8,
            "review_count": 2800,
            "price_per_person": {"currency": "GBP", "amount": 20.0},
            "price_details": {
                "adult_price": {"currency": "GBP", "amount": 20.0},
                "child_price": {"currency": "GBP", "amount": 10.0},
                "senior_price": {"currency": "GBP", "amount": 15.0},
            },
            "duration_minutes": 120,
            "available_times": [
                {"date": "2026-06-03", "time": "11:00", "available_spots": 15},
            ],
            "highlights": ["Ancient Egypt", "Rosetta Stone", "Greek artifacts"],
            "included": ["Museum entry", "Guide"],
            "excluded": ["Transport", "Food"],
            "min_participants": 1,
            "max_participants": 25,
            "difficulty_level": "easy",
            "hotel_pickup": False,
            "meal_included": False,
            "cancellation_policy": "12 hours before",
            "scores": {
                "price_score": 9.0,
                "quality_score": 9.5,
                "convenience_score": 8.5,
                "preference_score": 9.0,
            },
            "booking_url": "https://example.com/book/british_museum",
            "provider": "London Tours",
            "available": True,
            "image_urls": ["https://example.com/images/british_museum.jpg"],
        },
        {
            "id": "a3",
            "name": "Thames River Cruise",
            "description": "Relax on a scenic cruise along the River Thames and see London’s landmarks from the water.",
            "category": ActivityCategory.OUTDOOR,
            "location": {
                "city": "London",
                "country": "UK",
                "latitude": 51.5074,
                "longitude": -0.1278,
            },
            "distance_from_query_km": 2.5,
            "rating": 4.6,
            "review_count": 1500,
            "price_per_person": {"currency": "GBP", "amount": 25.0},
            "price_details": {
                "adult_price": {"currency": "GBP", "amount": 25.0},
                "child_price": {"currency": "GBP", "amount": 15.0},
                "senior_price": {"currency": "GBP", "amount": 20.0},
            },
            "duration_minutes": 90,
            "available_times": [
                {"date": "2026-06-04", "time": "14:00", "available_spots": 20},
            ],
            "highlights": ["Tower Bridge", "London Eye", "Big Ben"],
            "included": ["Cruise ticket", "Guide commentary"],
            "excluded": ["Meals", "Transport"],
            "min_participants": 1,
            "max_participants": 40,
            "difficulty_level": "easy",
            "hotel_pickup": True,
            "meal_included": False,
            "cancellation_policy": "24 hours before",
            "scores": {
                "price_score": 8.5,
                "quality_score": 9.0,
                "convenience_score": 9.0,
                "preference_score": 8.5,
            },
            "booking_url": "https://example.com/book/thames_cruise",
            "provider": "City Cruises",
            "available": True,
            "image_urls": ["https://example.com/images/thames_cruise.jpg"],
        },
        # Manchester Activities
        {
            "id": "a4",
            "name": "Old Trafford Stadium Tour",
            "description": "Visit the home of Manchester United and enjoy behind-the-scenes access.",
            "category": ActivityCategory.TOUR,
            "location": {
                "city": "Manchester",
                "country": "UK",
                "latitude": 53.4631,
                "longitude": -2.2913,
            },
            "distance_from_query_km": 1.0,
            "rating": 4.7,
            "review_count": 1800,
            "price_per_person": {"currency": "GBP", "amount": 30.0},
            "price_details": {
                "adult_price": {"currency": "GBP", "amount": 30.0},
                "child_price": {"currency": "GBP", "amount": 20.0},
                "senior_price": {"currency": "GBP", "amount": 25.0},
            },
            "duration_minutes": 90,
            "available_times": [
                {"date": "2026-06-16", "time": "10:00", "available_spots": 15},
            ],
            "highlights": ["Stadium tour", "Museum", "Locker rooms"],
            "included": ["Guide", "Entrance ticket"],
            "excluded": ["Transport", "Meals"],
            "min_participants": 1,
            "max_participants": 20,
            "difficulty_level": "easy",
            "hotel_pickup": False,
            "meal_included": False,
            "cancellation_policy": "24 hours before",
            "scores": {
                "price_score": 8.0,
                "quality_score": 9.0,
                "convenience_score": 8.5,
                "preference_score": 8.5,
            },
            "booking_url": "https://example.com/book/old_trafford",
            "provider": "Manchester Tours",
            "available": True,
            "image_urls": ["https://example.com/images/old_trafford.jpg"],
        },
    ]
}


def get_activities():
    return activities_packet["options"]
