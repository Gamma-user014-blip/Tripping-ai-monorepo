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

        # London
        {"name": "London Royal Inn", "city": "London", "country": "UK", "address": "10 Baker Street",
         "rating": 4.3, "review_count": 150, "all_inclusive": True, "amenities": ["wifi", "spa"], "room_type": "standard",
         "price_per_night": 180.0, "currency": "GBP", "free_cancellation": True, "check_in_time": "14:00",
         "check_out_time": "12:00", "latitude": 51.5200, "longitude": -0.1550},

        {"name": "Budget London Stay", "city": "London", "country": "UK", "address": "22 King’s Road",
         "rating": 3.8, "review_count": 60, "all_inclusive": False, "amenities": ["wifi"], "room_type": "standard",
         "price_per_night": 90.0, "currency": "GBP", "free_cancellation": False, "check_in_time": "14:00",
         "check_out_time": "12:00", "latitude": 51.5150, "longitude": -0.1400},

        {"name": "The Savoy Hotel", "city": "London", "country": "UK", "address": "Strand",
         "rating": 4.8, "review_count": 200, "all_inclusive": True, "amenities": ["wifi", "pool", "spa"], "room_type": "suite",
         "price_per_night": 350.0, "currency": "GBP", "free_cancellation": True, "check_in_time": "15:00",
         "check_out_time": "12:00", "latitude": 51.5100, "longitude": -0.1200},

        # New York
        {"name": "NY Downtown Hotel", "city": "New York", "country": "USA", "address": "1 Wall Street",
         "rating": 4.6, "review_count": 130, "all_inclusive": True, "amenities": ["wifi", "gym"], "room_type": "standard",
         "price_per_night": 220.0, "currency": "USD", "free_cancellation": True, "check_in_time": "15:00",
         "check_out_time": "12:00", "latitude": 40.7070, "longitude": -74.0113},

        {"name": "Midtown Comfort Inn", "city": "New York", "country": "USA", "address": "500 5th Ave",
         "rating": 4.1, "review_count": 95, "all_inclusive": False, "amenities": ["wifi"], "room_type": "standard",
         "price_per_night": 180.0, "currency": "USD", "free_cancellation": False, "check_in_time": "14:00",
         "check_out_time": "12:00", "latitude": 40.7530, "longitude": -73.9800}
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

