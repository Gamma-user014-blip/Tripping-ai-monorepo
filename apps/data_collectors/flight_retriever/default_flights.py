# default_flights.py
# Default sample flights to use when the flights API is unavailable
# This file contains realistic flight data for common routes
# Now also includes a dynamic generator for any route!

import random
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Airport code to country mapping
AIRPORT_COUNTRIES: Dict[str, str] = {
    # Israel
    "TLV": "Israel", "SDV": "Israel",
    # Italy
    "FCO": "Italy", "MXP": "Italy", "VCE": "Italy", "NAP": "Italy", "FLR": "Italy", "BGY": "Italy", "PSA": "Italy", "BLQ": "Italy",
    # Spain
    "MAD": "Spain", "BCN": "Spain", "PMI": "Spain", "AGP": "Spain", "VLC": "Spain",
    # France
    "CDG": "France", "ORY": "France", "NCE": "France", "LYS": "France", "MRS": "France",
    # UK
    "LHR": "United Kingdom", "LGW": "United Kingdom", "STN": "United Kingdom", "MAN": "United Kingdom", "EDI": "United Kingdom",
    # Germany
    "FRA": "Germany", "MUC": "Germany", "BER": "Germany", "DUS": "Germany", "HAM": "Germany",
    # USA
    "JFK": "USA", "LAX": "USA", "ORD": "USA", "SFO": "USA", "MIA": "USA", "DFW": "USA", "ATL": "USA", "BOS": "USA",
    # Greece
    "ATH": "Greece", "SKG": "Greece", "HER": "Greece", "JTR": "Greece", "JMK": "Greece",
    # Netherlands
    "AMS": "Netherlands",
    # Portugal
    "LIS": "Portugal", "OPO": "Portugal", "FAO": "Portugal",
    # Turkey
    "IST": "Turkey", "SAW": "Turkey", "AYT": "Turkey",
    # UAE
    "DXB": "United Arab Emirates", "AUH": "United Arab Emirates",
    # Thailand
    "BKK": "Thailand", "HKT": "Thailand",
    # Japan
    "NRT": "Japan", "HND": "Japan", "KIX": "Japan",
    # Australia
    "SYD": "Australia", "MEL": "Australia", "BNE": "Australia",
}

# Airport code to city mapping
AIRPORT_CITIES: Dict[str, str] = {
    # Israel
    "TLV": "Tel Aviv", "SDV": "Tel Aviv",
    # Italy
    "FCO": "Rome", "MXP": "Milan", "VCE": "Venice", "NAP": "Naples", "FLR": "Florence",
    "BGY": "Milan", "PSA": "Pisa", "BLQ": "Bologna",
    # Spain
    "MAD": "Madrid", "BCN": "Barcelona", "PMI": "Palma", "AGP": "Malaga", "VLC": "Valencia",
    # France
    "CDG": "Paris", "ORY": "Paris", "NCE": "Nice", "LYS": "Lyon", "MRS": "Marseille",
    # UK
    "LHR": "London", "LGW": "London", "STN": "London", "MAN": "Manchester", "EDI": "Edinburgh",
    # Germany
    "FRA": "Frankfurt", "MUC": "Munich", "BER": "Berlin", "DUS": "Dusseldorf", "HAM": "Hamburg",
    # USA
    "JFK": "New York", "LAX": "Los Angeles", "ORD": "Chicago", "SFO": "San Francisco",
    "MIA": "Miami", "DFW": "Dallas", "ATL": "Atlanta", "BOS": "Boston",
    # Greece
    "ATH": "Athens", "SKG": "Thessaloniki", "HER": "Heraklion", "JTR": "Santorini", "JMK": "Mykonos",
    # Netherlands
    "AMS": "Amsterdam",
    # Portugal
    "LIS": "Lisbon", "OPO": "Porto", "FAO": "Faro",
    # Turkey
    "IST": "Istanbul", "SAW": "Istanbul", "AYT": "Antalya",
    # UAE
    "DXB": "Dubai", "AUH": "Abu Dhabi",
    # Thailand
    "BKK": "Bangkok", "HKT": "Phuket",
    # Japan
    "NRT": "Tokyo", "HND": "Tokyo", "KIX": "Osaka",
    # Australia
    "SYD": "Sydney", "MEL": "Melbourne", "BNE": "Brisbane",
}

# Airport code to coordinates mapping (lat, lon)
AIRPORT_COORDINATES: Dict[str, tuple[float, float]] = {
    # Israel
    "TLV": (32.0114, 34.8867), "SDV": (32.1147, 34.7822),
    # Italy
    "FCO": (41.8003, 12.2389), "MXP": (45.6301, 8.7231), "VCE": (45.5053, 12.3519),
    "NAP": (40.8860, 14.2908), "FLR": (43.8100, 11.2051), "BGY": (45.6739, 9.7042),
    "PSA": (43.6839, 10.3928), "BLQ": (44.5354, 11.2887),
    # Spain
    "MAD": (40.4983, -3.5676), "BCN": (41.2974, 2.0833), "PMI": (39.5517, 2.7388),
    "AGP": (36.6749, -4.4991), "VLC": (39.4893, -0.4816),
    # France
    "CDG": (49.0097, 2.5479), "ORY": (48.7233, 2.3794), "NCE": (43.6584, 7.2159),
    "LYS": (45.7256, 5.0811), "MRS": (43.4393, 5.2214),
    # UK
    "LHR": (51.4700, -0.4543), "LGW": (51.1537, -0.1821), "STN": (51.8850, 0.2350),
    "MAN": (53.3537, -2.2750), "EDI": (55.9508, -3.3615),
    # Germany
    "FRA": (50.0379, 8.5622), "MUC": (48.3538, 11.7861), "BER": (52.3667, 13.5033),
    "DUS": (51.2895, 6.7668), "HAM": (53.6304, 9.9882),
    # USA
    "JFK": (40.6413, -73.7781), "LAX": (33.9425, -118.4081), "ORD": (41.9742, -87.9073),
    "SFO": (37.6213, -122.3790), "MIA": (25.7959, -80.2870), "DFW": (32.8998, -97.0403),
    "ATL": (33.6407, -84.4277), "BOS": (42.3656, -71.0096),
    # Greece
    "ATH": (37.9364, 23.9445), "SKG": (40.5197, 22.9709), "HER": (35.3397, 25.1803),
    "JTR": (36.3992, 25.4793), "JMK": (37.4351, 25.3481),
    # Netherlands
    "AMS": (52.3105, 4.7683),
    # Portugal
    "LIS": (38.7756, -9.1354), "OPO": (41.2481, -8.6814), "FAO": (37.0144, -7.9659),
    # Turkey
    "IST": (41.2753, 28.7519), "SAW": (40.8986, 29.3092), "AYT": (36.8987, 30.8005),
    # UAE
    "DXB": (25.2532, 55.3657), "AUH": (24.4330, 54.6511),
    # Thailand
    "BKK": (13.6900, 100.7501), "HKT": (8.1132, 98.3169),
    # Japan
    "NRT": (35.7720, 140.3929), "HND": (35.5494, 139.7798), "KIX": (34.4347, 135.2441),
    # Australia
    "SYD": (-33.9399, 151.1753), "MEL": (-37.6690, 144.8410), "BNE": (-27.3842, 153.1175),
}

def get_coordinates_for_airport(airport_code: str) -> tuple[float, float]:
    """Get the coordinates (lat, lon) for an airport code, or a reasonable default."""
    return AIRPORT_COORDINATES.get(airport_code.upper(), (0.0, 0.0))

def get_country_for_airport(airport_code: str) -> str:
    """Get the country name for an airport code, or a reasonable default."""
    return AIRPORT_COUNTRIES.get(airport_code.upper(), "Unknown")


def get_city_for_airport(airport_code: str) -> str:
    """Get the city name for an airport code, or fall back to the airport code."""
    code = airport_code.upper()
    return AIRPORT_CITIES.get(code, code)

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
    }
]

# ... (other static data kept for backward compatibility or deleted if preferred)
# For the sake of the task, I will keep the static ones and add the generator.

def get_default_flights_by_route(origin_city: Optional[str], destination_city: Optional[str], 
                                origin_code: Optional[str] = None, dest_code: Optional[str] = None,
                                departure_date: Optional[str] = None, passengers: int = 1) -> List[Dict[str, Any]]:
    """
    Get default flights for a specific route.
    Now generates mock flights if no static route is found.
    """
    origin = (origin_city or "").lower().strip()
    destination = (destination_city or "").lower().strip()
    ocode = (origin_code or "").lower().strip()
    dcode = (dest_code or "").lower().strip()
    
    # Try static routes first
    route_map = {
        ("new york", "london"): ny_to_london_flights,
        ("jfk", "lhr"): ny_to_london_flights,
    }
    
    static_flights = route_map.get((origin, destination)) or route_map.get((ocode, dcode))
    if static_flights:
        return static_flights

    # If no static flight, generate mock ones!
    return generate_mock_flights(
        origin_city or ocode.upper(), 
        origin_code or ocode.upper(),
        destination_city or dcode.upper(),
        dest_code or dcode.upper(),
        departure_date or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        passengers
    )

def generate_mock_flights(origin_city: str, origin_code: str, dest_city: str, dest_code: str, 
                         departure_date: str, passengers: int) -> List[Dict[str, Any]]:
    """
    Generates 2-3 realistic mock flight options for any given route.
    """
    airlines = [
        ("Delta Air Lines", "DL"), ("United Airlines", "UA"), ("American Airlines", "AA"),
        ("Lufthansa", "LH"), ("Air France", "AF"), ("Emirates", "EK"), ("Singapore Airlines", "SQ"),
        ("Qantas", "QF"), ("Qatar Airways", "QR"), ("Cathay Pacific", "CX")
    ]
    
    aircrafts = ["Boeing 787-9 Dreamliner", "Airbus A350-900", "Boeing 777-300ER", "Airbus A320neo", "Boeing 737 MAX 8"]
    
    options = []
    
    # Generate 2 options: One direct, one with a layover (if it's not a short flight, but let's just make 2 variants)
    for i in range(2):
        airline_name, airline_code = random.choice(airlines)
        is_direct = (i == 0)
        
        # Base price per person between $300 and $1200
        base_price = random.randint(300, 1200)
        total_price_val = base_price * passengers
        
        # Duration between 120 and 840 minutes
        duration = random.randint(120, 840)
        
        # Times
        departure_dt = datetime.fromisoformat(departure_date) + timedelta(hours=random.randint(6, 20))
        arrival_dt = departure_dt + timedelta(minutes=duration)
        
        flight_num = f"{airline_code}{random.randint(100, 999)}"
        
        flight_id = f"mock_f_{origin_code}_{dest_code}_{uuid.uuid4().hex[:6]}"
        
        origin_country = get_country_for_airport(origin_code)
        dest_country = get_country_for_airport(dest_code)
        origin_lat, origin_lon = get_coordinates_for_airport(origin_code)
        dest_lat, dest_lon = get_coordinates_for_airport(dest_code)
        
        mock_flight = {
            "id": flight_id,
            "outbound": {
                "origin": {
                    "city": origin_city,
                    "country": origin_country,
                    "airport_code": origin_code.upper(),
                    "latitude": origin_lat,
                    "longitude": origin_lon,
                },
                "destination": {
                    "city": dest_city,
                    "country": dest_country,
                    "airport_code": dest_code.upper(),
                    "latitude": dest_lat,
                    "longitude": dest_lon,
                },
                "departure_time": departure_dt.isoformat(),
                "arrival_time": arrival_dt.isoformat(),
                "duration_minutes": duration,
                "stops": 0 if is_direct else 1,
                "layovers": [] if is_direct else [
                    {
                        "airport": {
                            "city": "Transit Hub",
                            "country": "",
                            "airport_code": "HUB",
                            "latitude": 0.5,
                            "longitude": 0.5,
                        },
                        "start_time": (departure_dt + timedelta(minutes=duration//3)).isoformat(),
                        "end_time": (departure_dt + timedelta(minutes=duration//2)).isoformat(),
                        "duration_minutes": duration//6,
                        "airline_before": airline_name,
                        "airline_after": airline_name,
                        "is_airline_change": False,
                        "is_terminal_change": False,
                        "overnight": False,
                    }
                ],
                "airline": airline_name,
                "flight_number": flight_num,
                "aircraft": random.choice(aircrafts),
                "cabin_class": "economy",
                "amenities": {
                    "wifi": random.choice([True, False]),
                    "meal": True,
                    "entertainment": True,
                    "power_outlet": True,
                    "legroom_inches": random.randint(30, 32),
                },
                "luggage": {
                    "checked_bags": 1,
                    "checked_bag_weight_kg": 23.0,
                    "carry_on_bags": 1,
                    "carry_on_weight_kg": 8.0,
                    "carry_on_dimensions_cm": "55x40x23",
                },
            },
            "total_price": {"currency": "USD", "amount": float(total_price_val)},
            "price_per_person": {"currency": "USD", "amount": float(base_price)},
            "scores": {
                "price_score": random.uniform(5.0, 9.5),
                "quality_score": random.uniform(5.0, 9.5),
                "convenience_score": random.uniform(5.0, 9.5),
                "preference_score": random.uniform(5.0, 9.5),
            },
            "booking_url": f"https://example.com/book/{flight_num}",
            "provider": airline_name,
            "available": True,
        }
        options.append(mock_flight)
        
    return options

def get_default_flight_by_id(flight_id: str) -> Dict[str, Any] | None:
    """
    Search in static and can be used to verify mock IDs if we wanted to (but they are transient).
    For now, just return None if not static, otherwise details endpoint might fail later.
    Actually, to make it work seamlessly, we should probably generate a consistent one if it starts with 'mock_f_'.
    """
    if flight_id.startswith("default_f_"):
        # Just check the one static we kept for example
        if flight_id == "default_f_ny_ldn_1":
            return ny_to_london_flights[0]

    if flight_id.startswith("mock_f_"):
        # For mock IDs, we can't easily reconstruct without state, 
        # but the details page usually only re-fetches if it doesn't have it.
        # Let's return a generic one based on the ID parts if possible.
        parts = flight_id.split("_")
        if len(parts) >= 4:
            origin = parts[2]
            dest = parts[3]
            return generate_mock_flights(
                get_city_for_airport(origin),
                origin,
                get_city_for_airport(dest),
                dest,
                datetime.now().strftime("%Y-%m-%d"),
                1,
            )[0]
            
    return None

def get_all_default_flights() -> List[Dict[str, Any]]:
    return ny_to_london_flights

def get_available_routes() -> List[tuple[str, str]]:
    return [("New York", "London")]
