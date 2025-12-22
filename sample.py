hotels_packet = {
    "hotels": [
        # Paris
        {"name": "Hotel Sunshine", "city": "Paris", "country": "France", "address": "123 Champs-Élysées",
         "rating": 4.5, "review_count": 120, "all_inclusive": True, "amenities": ["wifi", "pool"], "room_type": "standard",
         "price_per_night": 150.0, "currency": "EUR", "free_cancellation": True, "check_in_time": "14:00",
         "check_out_time": "12:00", "latitude": 48.8566, "longitude": 2.3522},

        {"name": "Grand Paris Hotel", "city": "Paris", "country": "France", "address": "456 Rue de Rivoli",
         "rating": 4.0, "review_count": 80, "all_inclusive": False, "amenities": ["wifi"], "room_type": "deluxe",
         "price_per_night": 120.0, "currency": "EUR", "free_cancellation": False, "check_in_time": "14:00",
         "check_out_time": "12:00", "latitude": 48.8600, "longitude": 2.3400},

        {"name": "Hotel de Louvre", "city": "Paris", "country": "France", "address": "99 Rue de Louvre",
         "rating": 4.2, "review_count": 90, "all_inclusive": False, "amenities": ["wifi", "gym"], "room_type": "suite",
         "price_per_night": 200.0, "currency": "EUR", "free_cancellation": True, "check_in_time": "14:00",
         "check_out_time": "12:00", "latitude": 48.8610, "longitude": 2.3350},

        # Other French cities
        {"name": "Nice Beach Resort", "city": "Nice", "country": "France", "address": "50 Promenade des Anglais",
         "rating": 4.4, "review_count": 110, "all_inclusive": True, "amenities": ["wifi", "pool"], "room_type": "deluxe",
         "price_per_night": 180.0, "currency": "EUR", "free_cancellation": True, "check_in_time": "15:00",
         "check_out_time": "12:00", "latitude": 43.6950, "longitude": 7.2700},

        {"name": "Lyon Central Hotel", "city": "Lyon", "country": "France", "address": "10 Rue de la République",
         "rating": 4.1, "review_count": 75, "all_inclusive": False, "amenities": ["wifi"], "room_type": "standard",
         "price_per_night": 130.0, "currency": "EUR", "free_cancellation": False, "check_in_time": "14:00",
         "check_out_time": "12:00", "latitude": 45.7640, "longitude": 4.8357},

        {"name": "Marseille Seaside Hotel", "city": "Marseille", "country": "France", "address": "22 Vieux-Port",
         "rating": 4.3, "review_count": 85, "all_inclusive": True, "amenities": ["wifi", "pool"], "room_type": "suite",
         "price_per_night": 160.0, "currency": "EUR", "free_cancellation": True, "check_in_time": "14:00",
         "check_out_time": "12:00", "latitude": 43.2965, "longitude": 5.3698}
    ]
}

flights_packet = {
    "flights": [
        # NYC → Paris (direct)
        {"route": {"from_airport": "JFK", "from_city": "New York", "from_country": "USA", "from_address": "JFK Airport",
                   "to_airport": "CDG", "to_city": "Paris", "to_country": "France", "to_address": "Charles de Gaulle Airport",
                   "depart_time": "2025-12-20T08:00:00Z", "arrival_time": "2025-12-20T20:00:00Z",
                   "airline": "Air France", "from_latitude": 40.6413, "from_longitude": -73.7781,
                   "to_latitude": 49.0097, "to_longitude": 2.5479},
         "connections": 0, "price": 650.0, "currency": "USD"},

        {"route": {"from_airport": "JFK", "from_city": "New York", "from_country": "USA", "from_address": "JFK Airport",
                   "to_airport": "ORY", "to_city": "Paris", "to_country": "France", "to_address": "Orly Airport",
                   "depart_time": "2025-12-21T09:00:00Z", "arrival_time": "2025-12-21T21:00:00Z",
                   "airline": "Delta", "from_latitude": 40.6413, "from_longitude": -73.7781,
                   "to_latitude": 48.7233, "to_longitude": 2.3797},
         "connections": 0, "price": 620.0, "currency": "USD"},

        # London → Paris (direct)
        {"route": {"from_airport": "LHR", "from_city": "London", "from_country": "UK", "from_address": "Heathrow Airport",
                   "to_airport": "CDG", "to_city": "Paris", "to_country": "France", "to_address": "Charles de Gaulle Airport",
                   "depart_time": "2025-12-21T09:00:00Z", "arrival_time": "2025-12-21T11:00:00Z",
                   "airline": "British Airways", "from_latitude": 51.4700, "from_longitude": -0.4543,
                   "to_latitude": 49.0097, "to_longitude": 2.5479},
         "connections": 0, "price": 120.0, "currency": "GBP"},

        {"route": {"from_airport": "LHR", "from_city": "London", "from_country": "UK", "from_address": "Heathrow Airport",
                   "to_airport": "LGW", "to_city": "London", "to_country": "UK", "to_address": "Gatwick Airport",
                   "depart_time": "2025-12-21T15:00:00Z", "arrival_time": "2025-12-21T16:00:00Z",
                   "airline": "EasyJet", "from_latitude": 51.4700, "from_longitude": -0.4543,
                   "to_latitude": 51.1537, "to_longitude": -0.1821},
         "connections": 0, "price": 60.0, "currency": "GBP"},

        # London → New York (direct)
        {"route": {"from_airport": "LHR", "from_city": "London", "from_country": "UK", "from_address": "Heathrow Airport",
                   "to_airport": "JFK", "to_city": "New York", "to_country": "USA", "to_address": "JFK Airport",
                   "depart_time": "2025-12-22T10:00:00Z", "arrival_time": "2025-12-22T20:00:00Z",
                   "airline": "British Airways", "from_latitude": 51.4700, "from_longitude": -0.4543,
                   "to_latitude": 40.6413, "to_longitude": -73.7781},
         "connections": 0, "price": 550.0, "currency": "GBP"},

        # Connecting flight: NYC → London → Paris
        {"route": {"from_airport": "JFK", "from_city": "New York", "from_country": "USA", "from_address": "JFK Airport",
                   "to_airport": "CDG", "to_city": "Paris", "to_country": "France", "to_address": "Charles de Gaulle Airport",
                   "depart_time": "2025-12-20T07:00:00Z", "arrival_time": "2025-12-20T22:00:00Z",
                   "airline": "British Airways", "from_latitude": 40.6413, "from_longitude": -73.7781,
                   "to_latitude": 49.0097, "to_longitude": 2.5479,
                   "via": [{"airport": "LHR", "city": "London", "country": "UK", "arrival_time": "2025-12-20T17:00:00Z",
                            "departure_time": "2025-12-20T18:00:00Z"}]},
         "connections": 1, "price": 580.0, "currency": "USD"},

        # Connecting flight: Paris → Amsterdam → Berlin
        {"route": {"from_airport": "CDG", "from_city": "Paris", "from_country": "France", "from_address": "Charles de Gaulle Airport",
                   "to_airport": "BER", "to_city": "Berlin", "to_country": "Germany", "to_address": "Berlin Brandenburg Airport",
                   "depart_time": "2025-12-23T06:00:00Z", "arrival_time": "2025-12-23T12:00:00Z",
                   "airline": "KLM", "from_latitude": 49.0097, "from_longitude": 2.5479,
                   "to_latitude": 52.3667, "to_longitude": 13.5033,
                   "via": [{"airport": "AMS", "city": "Amsterdam", "country": "Netherlands", "arrival_time": "2025-12-23T09:00:00Z",
                            "departure_time": "2025-12-23T10:00:00Z"}]},
         "connections": 1, "price": 220.0, "currency": "EUR"}
    ]
}

