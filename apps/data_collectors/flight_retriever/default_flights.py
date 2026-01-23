# default_flights.py
# Default sample flights to use when the flights API is unavailable
# This file contains realistic flight data for common routes

from typing import List, Dict, Any

# ======================
# POPULAR ROUTES
# ======================

# New York to London
ny_to_london_flights = [
    {
        "id": "default_f_ny_ldn_1",
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
            "arrival_time": "2026-06-01T22:00:00",
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
        "total_price": {"currency": "USD", "amount": 1600.0},
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
        "id": "default_f_ny_ldn_2",
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
            "departure_time": "2026-06-01T14:30:00",
            "arrival_time": "2026-06-02T02:30:00",
            "duration_minutes": 480,
            "stops": 0,
            "layovers": [],
            "airline": "Virgin Atlantic",
            "flight_number": "VS4",
            "aircraft": "Airbus A350-1000",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": True,
                "entertainment": True,
                "power_outlet": True,
                "legroom_inches": 32,
            },
            "luggage": {
                "checked_bags": 1,
                "checked_bag_weight_kg": 23.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 10.0,
                "carry_on_dimensions_cm": "56x36x23",
            },
        },
        "total_price": {"currency": "USD", "amount": 1400.0},
        "price_per_person": {"currency": "USD", "amount": 700.0},
        "scores": {
            "price_score": 8.0,
            "quality_score": 8.5,
            "convenience_score": 8.0,
            "preference_score": 8.0,
        },
        "booking_url": "https://example.com/book/VS4",
        "provider": "Virgin Atlantic",
        "available": True,
    },
]

# London to New York (Return)
london_to_ny_flights = [
    {
        "id": "default_f_ldn_ny_1",
        "outbound": {
            "origin": {
                "city": "London",
                "country": "UK",
                "airport_code": "LHR",
                "latitude": 51.4700,
                "longitude": -0.4543,
            },
            "destination": {
                "city": "New York",
                "country": "USA",
                "airport_code": "JFK",
                "latitude": 40.6413,
                "longitude": -73.7781,
            },
            "departure_time": "2026-06-15T11:00:00",
            "arrival_time": "2026-06-15T14:00:00",
            "duration_minutes": 480,
            "stops": 0,
            "layovers": [],
            "airline": "British Airways",
            "flight_number": "BA177",
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
        "total_price": {"currency": "USD", "amount": 1500.0},
        "price_per_person": {"currency": "USD", "amount": 750.0},
        "scores": {
            "price_score": 7.8,
            "quality_score": 9.0,
            "convenience_score": 9.5,
            "preference_score": 8.5,
        },
        "booking_url": "https://example.com/book/BA177",
        "provider": "British Airways",
        "available": True,
    },
]

# Los Angeles to Tokyo
la_to_tokyo_flights = [
    {
        "id": "default_f_la_tokyo_1",
        "outbound": {
            "origin": {
                "city": "Los Angeles",
                "country": "USA",
                "airport_code": "LAX",
                "latitude": 33.9416,
                "longitude": -118.4085,
            },
            "destination": {
                "city": "Tokyo",
                "country": "Japan",
                "airport_code": "NRT",
                "latitude": 35.7720,
                "longitude": 140.3929,
            },
            "departure_time": "2026-07-01T11:00:00",
            "arrival_time": "2026-07-02T15:00:00",
            "duration_minutes": 660,
            "stops": 0,
            "layovers": [],
            "airline": "Japan Airlines",
            "flight_number": "JL61",
            "aircraft": "Boeing 787-9",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": True,
                "entertainment": True,
                "power_outlet": True,
                "legroom_inches": 33,
            },
            "luggage": {
                "checked_bags": 2,
                "checked_bag_weight_kg": 23.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 10.0,
                "carry_on_dimensions_cm": "55x40x25",
            },
        },
        "total_price": {"currency": "USD", "amount": 2400.0},
        "price_per_person": {"currency": "USD", "amount": 1200.0},
        "scores": {
            "price_score": 7.0,
            "quality_score": 9.5,
            "convenience_score": 9.0,
            "preference_score": 9.0,
        },
        "booking_url": "https://example.com/book/JL61",
        "provider": "Japan Airlines",
        "available": True,
    },
]

# Paris to Barcelona
paris_to_barcelona_flights = [
    {
        "id": "default_f_paris_bcn_1",
        "outbound": {
            "origin": {
                "city": "Paris",
                "country": "France",
                "airport_code": "CDG",
                "latitude": 49.0097,
                "longitude": 2.5479,
            },
            "destination": {
                "city": "Barcelona",
                "country": "Spain",
                "airport_code": "BCN",
                "latitude": 41.2974,
                "longitude": 2.0833,
            },
            "departure_time": "2026-08-10T08:30:00",
            "arrival_time": "2026-08-10T10:30:00",
            "duration_minutes": 120,
            "stops": 0,
            "layovers": [],
            "airline": "Air France",
            "flight_number": "AF1148",
            "aircraft": "Airbus A320",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": False,
                "entertainment": False,
                "power_outlet": False,
                "legroom_inches": 30,
            },
            "luggage": {
                "checked_bags": 1,
                "checked_bag_weight_kg": 23.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 12.0,
                "carry_on_dimensions_cm": "55x35x25",
            },
        },
        "total_price": {"currency": "EUR", "amount": 300.0},
        "price_per_person": {"currency": "EUR", "amount": 150.0},
        "scores": {
            "price_score": 8.5,
            "quality_score": 8.0,
            "convenience_score": 9.0,
            "preference_score": 8.0,
        },
        "booking_url": "https://example.com/book/AF1148",
        "provider": "Air France",
        "available": True,
    },
]

# Dubai to Singapore
dubai_to_singapore_flights = [
    {
        "id": "default_f_dubai_sing_1",
        "outbound": {
            "origin": {
                "city": "Dubai",
                "country": "UAE",
                "airport_code": "DXB",
                "latitude": 25.2532,
                "longitude": 55.3657,
            },
            "destination": {
                "city": "Singapore",
                "country": "Singapore",
                "airport_code": "SIN",
                "latitude": 1.3644,
                "longitude": 103.9915,
            },
            "departure_time": "2026-09-05T03:00:00",
            "arrival_time": "2026-09-05T14:30:00",
            "duration_minutes": 450,
            "stops": 0,
            "layovers": [],
            "airline": "Emirates",
            "flight_number": "EK354",
            "aircraft": "Airbus A380",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": True,
                "entertainment": True,
                "power_outlet": True,
                "legroom_inches": 32,
            },
            "luggage": {
                "checked_bags": 2,
                "checked_bag_weight_kg": 30.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 7.0,
                "carry_on_dimensions_cm": "55x38x20",
            },
        },
        "total_price": {"currency": "USD", "amount": 1800.0},
        "price_per_person": {"currency": "USD", "amount": 900.0},
        "scores": {
            "price_score": 8.0,
            "quality_score": 9.5,
            "convenience_score": 9.0,
            "preference_score": 9.0,
        },
        "booking_url": "https://example.com/book/EK354",
        "provider": "Emirates",
        "available": True,
    },
]

# Sydney to Melbourne (Domestic)
sydney_to_melbourne_flights = [
    {
        "id": "default_f_syd_mel_1",
        "outbound": {
            "origin": {
                "city": "Sydney",
                "country": "Australia",
                "airport_code": "SYD",
                "latitude": -33.9399,
                "longitude": 151.1753,
            },
            "destination": {
                "city": "Melbourne",
                "country": "Australia",
                "airport_code": "MEL",
                "latitude": -37.6690,
                "longitude": 144.8410,
            },
            "departure_time": "2026-10-12T09:00:00",
            "arrival_time": "2026-10-12T10:30:00",
            "duration_minutes": 90,
            "stops": 0,
            "layovers": [],
            "airline": "Qantas",
            "flight_number": "QF401",
            "aircraft": "Boeing 737-800",
            "cabin_class": "economy",
            "amenities": {
                "wifi": True,
                "meal": False,
                "entertainment": True,
                "power_outlet": True,
                "legroom_inches": 30,
            },
            "luggage": {
                "checked_bags": 1,
                "checked_bag_weight_kg": 23.0,
                "carry_on_bags": 1,
                "carry_on_weight_kg": 7.0,
                "carry_on_dimensions_cm": "56x36x23",
            },
        },
        "total_price": {"currency": "AUD", "amount": 400.0},
        "price_per_person": {"currency": "AUD", "amount": 200.0},
        "scores": {
            "price_score": 7.5,
            "quality_score": 8.5,
            "convenience_score": 9.5,
            "preference_score": 8.0,
        },
        "booking_url": "https://example.com/book/QF401",
        "provider": "Qantas",
        "available": True,
    },
]

# Budget option with layover - New York to London via Dublin
ny_to_london_budget = [
    {
        "id": "default_f_ny_ldn_budget_1",
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
            "departure_time": "2026-06-01T18:00:00",
            "arrival_time": "2026-06-02T11:30:00",
            "duration_minutes": 690,
            "stops": 1,
            "layovers": [
                {
                    "airport": {
                        "city": "Dublin",
                        "country": "Ireland",
                        "airport_code": "DUB",
                        "latitude": 53.4213,
                        "longitude": -6.2701,
                    },
                    "start_time": "2026-06-02T06:00:00",
                    "end_time": "2026-06-02T08:30:00",
                    "duration_minutes": 150,
                    "arrival_terminal": "2",
                    "departure_terminal": "2",
                    "airline_before": "Aer Lingus",
                    "airline_after": "Aer Lingus",
                    "is_airline_change": False,
                    "is_terminal_change": False,
                    "overnight": False,
                }
            ],
            "airline": "Aer Lingus",
            "flight_number": "EI104",
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
                "carry_on_weight_kg": 10.0,
                "carry_on_dimensions_cm": "55x40x24",
            },
        },
        "total_price": {"currency": "USD", "amount": 1000.0},
        "price_per_person": {"currency": "USD", "amount": 500.0},
        "scores": {
            "price_score": 9.0,
            "quality_score": 7.5,
            "convenience_score": 6.5,
            "preference_score": 7.0,
        },
        "booking_url": "https://example.com/book/EI104",
        "provider": "Aer Lingus",
        "available": True,
    },
]

# ======================
# HELPER FUNCTIONS
# ======================

def get_default_flights_by_route(origin_city: str, destination_city: str) -> List[Dict[str, Any]]:
    """
    Get default flights for a specific route.
    
    Args:
        origin_city: Origin city name (case-insensitive)
        destination_city: Destination city name (case-insensitive)
    
    Returns:
        List of flight options for the route, or empty list if route not found
    """
    origin = origin_city.lower().strip()
    destination = destination_city.lower().strip()
    
    route_map = {
        ("new york", "london"): ny_to_london_flights + ny_to_london_budget,
        ("jfk", "lhr"): ny_to_london_flights + ny_to_london_budget,
        
        ("london", "new york"): london_to_ny_flights,
        ("lhr", "jfk"): london_to_ny_flights,
        
        ("los angeles", "tokyo"): la_to_tokyo_flights,
        ("lax", "nrt"): la_to_tokyo_flights,
        
        ("paris", "barcelona"): paris_to_barcelona_flights,
        ("cdg", "bcn"): paris_to_barcelona_flights,
        
        ("dubai", "singapore"): dubai_to_singapore_flights,
        ("dxb", "sin"): dubai_to_singapore_flights,
        
        ("sydney", "melbourne"): sydney_to_melbourne_flights,
        ("syd", "mel"): sydney_to_melbourne_flights,
    }
    
    return route_map.get((origin, destination), [])


def get_all_default_flights() -> List[Dict[str, Any]]:
    """
    Get all available default flights.
    
    Returns:
        List of all default flight options
    """
    all_flights = []
    all_flights.extend(ny_to_london_flights)
    all_flights.extend(ny_to_london_budget)
    all_flights.extend(london_to_ny_flights)
    all_flights.extend(la_to_tokyo_flights)
    all_flights.extend(paris_to_barcelona_flights)
    all_flights.extend(dubai_to_singapore_flights)
    all_flights.extend(sydney_to_melbourne_flights)
    return all_flights


def get_default_flight_by_id(flight_id: str) -> Dict[str, Any] | None:
    """
    Get a specific default flight by its ID.
    
    Args:
        flight_id: The flight ID to search for
    
    Returns:
        Flight data dict if found, None otherwise
    """
    all_flights = get_all_default_flights()
    for flight in all_flights:
        if flight["id"] == flight_id:
            return flight
    return None


def get_available_routes() -> List[tuple[str, str]]:
    """
    Get list of all available default routes.
    
    Returns:
        List of (origin_city, destination_city) tuples
    """
    return [
        ("New York", "London"),
        ("London", "New York"),
        ("Los Angeles", "Tokyo"),
        ("Paris", "Barcelona"),
        ("Dubai", "Singapore"),
        ("Sydney", "Melbourne"),
    ]
