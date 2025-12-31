hotels_packet = {
  "options": [
    {
      "id": "london_central_hotel",
      "name": "London Central Hotel",
      "description": "Upscale hotel in central London, close to Heathrow Airport.",
      "location": {
        "city": "London",
        "country": "UK",
        "airport_code": "LHR",
        "latitude": 51.5074,
        "longitude": -0.1278
      },
      "distance_to_center_km": 0.5,
      "rating": 4.6,
      "review_count": 200,
      "rating_category": "Excellent",
      "price_per_night": {
        "currency": "GBP",
        "amount": 250.0
      },
      "total_price": {
        "currency": "GBP",
        "amount": 1250.0
      },
      "additional_fees": [],
      "room": {
        "type": "Deluxe",
        "beds": 2,
        "bed_type": "Queen",
        "max_occupancy": 3,
        "size_sqm": 28.0,
        "features": ["City view"]
      },
      "amenities": ["wifi", "gym", "pool"],
      "category": "upscale",
      "star_rating": 5,
      "scores": {
        "price_score": 0.8,
        "quality_score": 0.9,
        "convenience_score": 0.85,
        "preference_score": 0.88
      },
      "booking_url": "https://booking.example.com/london_central_hotel",
      "provider": "mock_provider",
      "available": True
    },
    {
      "id": "heathrow_express_hotel",
      "name": "Heathrow Express Hotel",
      "description": "Business-friendly hotel near Heathrow Airport.",
      "location": {
        "city": "London",
        "country": "UK",
        "airport_code": "LHR",
        "latitude": 51.4700,
        "longitude": -0.4543
      },
      "distance_to_center_km": 0.2,
      "rating": 4.3,
      "review_count": 150,
      "rating_category": "Very Good",
      "price_per_night": {
        "currency": "GBP",
        "amount": 180.0
      },
      "total_price": {
        "currency": "GBP",
        "amount": 900.0
      },
      "additional_fees": [],
      "room": {
        "type": "Standard",
        "beds": 1,
        "bed_type": "King",
        "max_occupancy": 2,
        "size_sqm": 22.0,
        "features": ["Airport view"]
      },
      "amenities": ["wifi", "breakfast"],
      "category": "midscale",
      "star_rating": 4,
      "scores": {
        "price_score": 0.85,
        "quality_score": 0.82,
        "convenience_score": 0.9,
        "preference_score": 0.8
      },
      "booking_url": "https://booking.example.com/heathrow_express_hotel",
      "provider": "mock_provider",
      "available": True
    },
    {
      "id": "soho_london_inn",
      "name": "Soho London Inn",
      "description": "Charming boutique hotel in Soho, London.",
      "location": {
        "city": "London",
        "country": "UK",
        "airport_code": "LHR",
        "latitude": 51.5136,
        "longitude": -0.1365
      },
      "distance_to_center_km": 0.7,
      "rating": 4.1,
      "review_count": 110,
      "rating_category": "Very Good",
      "price_per_night": {
        "currency": "GBP",
        "amount": 160.0
      },
      "total_price": {
        "currency": "GBP",
        "amount": 800.0
      },
      "additional_fees": [],
      "room": {
        "type": "Standard",
        "beds": 1,
        "bed_type": "Queen",
        "max_occupancy": 2,
        "size_sqm": 18.0,
        "features": ["City view"]
      },
      "amenities": ["wifi", "breakfast"],
      "category": "midscale",
      "star_rating": 3,
      "scores": {
        "price_score": 0.88,
        "quality_score": 0.78,
        "convenience_score": 0.8,
        "preference_score": 0.82
      },
      "booking_url": "https://booking.example.com/soho_london_inn",
      "provider": "mock_provider",
      "available": True
    },
    {
      "id": "kensington_suite",
      "name": "Kensington Suite Hotel",
      "description": "Luxury suite hotel near Kensington Gardens.",
      "location": {
        "city": "London",
        "country": "UK",
        "airport_code": "LHR",
        "latitude": 51.5010,
        "longitude": -0.1740
      },
      "distance_to_center_km": 1.5,
      "rating": 4.7,
      "review_count": 220,
      "rating_category": "Excellent",
      "price_per_night": {
        "currency": "GBP",
        "amount": 320.0
      },
      "total_price": {
        "currency": "GBP",
        "amount": 1600.0
      },
      "additional_fees": [],
      "room": {
        "type": "Suite",
        "beds": 2,
        "bed_type": "King",
        "max_occupancy": 3,
        "size_sqm": 40.0,
        "features": ["Balcony", "City view"]
      },
      "amenities": ["wifi", "pool", "gym"],
      "category": "luxury",
      "star_rating": 5,
      "scores": {
        "price_score": 0.75,
        "quality_score": 0.92,
        "convenience_score": 0.87,
        "preference_score": 0.9
      },
      "booking_url": "https://booking.example.com/kensington_suite",
      "provider": "mock_provider",
      "available": True
    },
    {
      "id": "heathrow_budget_inn",
      "name": "Heathrow Budget Inn",
      "description": "Budget-friendly hotel near Heathrow Airport.",
      "location": {
        "city": "London",
        "country": "UK",
        "airport_code": "LHR",
        "latitude": 51.4660,
        "longitude": -0.4500
      },
      "distance_to_center_km": 0.3,
      "rating": 3.8,
      "review_count": 90,
      "rating_category": "Good",
      "price_per_night": {
        "currency": "GBP",
        "amount": 120.0
      },
      "total_price": {
        "currency": "GBP",
        "amount": 600.0
      },
      "additional_fees": [],
      "room": {
        "type": "Standard",
        "beds": 1,
        "bed_type": "Twin",
        "max_occupancy": 2,
        "size_sqm": 16.0,
        "features": []
      },
      "amenities": ["wifi"],
      "category": "budget",
      "star_rating": 3,
      "scores": {
        "price_score": 0.9,
        "quality_score": 0.7,
        "convenience_score": 0.8,
        "preference_score": 0.75
      },
      "booking_url": "https://booking.example.com/heathrow_budget_inn",
      "provider": "mock_provider",
      "available": True
    },
    {
      "id": "victoria_park_hotel",
      "name": "Victoria Park Hotel",
      "description": "Comfortable hotel in east London, ideal for travelers.",
      "location": {
        "city": "London",
        "country": "UK",
        "airport_code": "LHR",
        "latitude": 51.5280,
        "longitude": -0.0810
      },
      "distance_to_center_km": 2.0,
      "rating": 4.2,
      "review_count": 130,
      "rating_category": "Very Good",
      "price_per_night": {
        "currency": "GBP",
        "amount": 140.0
      },
      "total_price": {
        "currency": "GBP",
        "amount": 700.0
      },
      "additional_fees": [],
      "room": {
        "type": "Standard",
        "beds": 1,
        "bed_type": "Queen",
        "max_occupancy": 2,
        "size_sqm": 18.0,
        "features": []
      },
      "amenities": ["wifi", "breakfast"],
      "category": "midscale",
      "star_rating": 4,
      "scores": {
        "price_score": 0.87,
        "quality_score": 0.8,
        "convenience_score": 0.82,
        "preference_score": 0.81
      },
      "booking_url": "https://booking.example.com/victoria_park_hotel",
      "provider": "mock_provider",
      "available": True
    },
    {
      "id": "earls_court_hotel",
      "name": "Earls Court Hotel",
      "description": "Affordable hotel near Earls Court with good transport links.",
      "location": {
        "city": "London",
        "country": "UK",
        "airport_code": "LHR",
        "latitude": 51.4940,
        "longitude": -0.1960
      },
      "distance_to_center_km": 1.8,
      "rating": 3.9,
      "review_count": 95,
      "rating_category": "Good",
      "price_per_night": {
        "currency": "GBP",
        "amount": 130.0
      },
      "total_price": {
        "currency": "GBP",
        "amount": 650.0
      },
      "additional_fees": [],
      "room": {
        "type": "Standard",
        "beds": 1,
        "bed_type": "Queen",
        "max_occupancy": 2,
        "size_sqm": 18.0,
        "features": []
      },
      "amenities": ["wifi", "breakfast"],
      "category": "budget",
      "star_rating": 3,
      "scores": {
        "price_score": 0.88,
        "quality_score": 0.75,
        "convenience_score": 0.8,
        "preference_score": 0.77
      },
      "booking_url": "https://booking.example.com/earls_court_hotel",
      "provider": "mock_provider",
      "available": True
    }
  ],
  "metadata": {
    "total_results": 7,
    "search_id": "hotel_search_london_2025",
    "timestamp": "2025-10-01T12:15:00Z",
    "data_source": "mock_data"
  }
}


flights_packet = {
    "options": [
        {
            "id": "f1",
            "outbound": {
                "origin": {"city": "New York", "country": "USA", "airport_code": "JFK", "latitude": 40.6413, "longitude": -73.7781},
                "destination": {"city": "London", "country": "UK", "airport_code": "LHR", "latitude": 51.4700, "longitude": -0.4543},
                "departure_time": "2025-12-20T08:00:00",
                "arrival_time": "2025-12-20T20:00:00",
                "duration_minutes": 720,
                "stops": 0,
                "layovers": [],
                "airline": "British Airways",
                "flight_number": "BA178",
                "aircraft": "B777",
                "cabin_class": "economy",
                "amenities": {"wifi": True, "meal": True, "entertainment": True, "power_outlet": True, "legroom_inches": 31}
            },
            "return": None,
            "total_price": {"currency": "USD", "amount": 650.0},
            "price_per_person": {"currency": "USD", "amount": 650.0},
            "scores": {},
            "booking_url": "https://book.britishairways.com/f1",
            "provider": "British Airways",
            "available": True
        },
        {
            "id": "f2",
            "outbound": {
                "origin": {"city": "New York", "country": "USA", "airport_code": "JFK", "latitude": 40.6413, "longitude": -73.7781},
                "destination": {"city": "London", "country": "UK", "airport_code": "LHR", "latitude": 51.4700, "longitude": -0.4543},
                "departure_time": "2025-12-20T09:30:00",
                "arrival_time": "2025-12-20T22:00:00",
                "duration_minutes": 690,
                "stops": 1,
                "layovers": [{"airport": {"city": "Dublin", "country": "Ireland", "airport_code": "DUB", "latitude": 53.4213, "longitude": -6.2701}, "duration_minutes": 60}],
                "airline": "Delta",
                "flight_number": "DL1",
                "aircraft": "A330",
                "cabin_class": "economy",
                "amenities": {"wifi": True, "meal": True, "entertainment": False, "power_outlet": False, "legroom_inches": 30}
            },
            "return": None,
            "total_price": {"currency": "USD", "amount": 620.0},
            "price_per_person": {"currency": "USD", "amount": 620.0},
            "scores": {},
            "booking_url": "https://book.delta.com/f2",
            "provider": "Delta",
            "available": True
        },
        {
            "id": "f3",
            "outbound": {
                "origin": {"city": "New York", "country": "USA", "airport_code": "JFK", "latitude": 40.6413, "longitude": -73.7781},
                "destination": {"city": "London", "country": "UK", "airport_code": "LHR", "latitude": 51.4700, "longitude": -0.4543},
                "departure_time": "2025-12-20T11:00:00",
                "arrival_time": "2025-12-20T23:00:00",
                "duration_minutes": 720,
                "stops": 0,
                "layovers": [],
                "airline": "American Airlines",
                "flight_number": "AA100",
                "aircraft": "B777",
                "cabin_class": "premium_economy",
                "amenities": {"wifi": True, "meal": True, "entertainment": True, "power_outlet": True, "legroom_inches": 33}
            },
            "return": None,
            "total_price": {"currency": "USD", "amount": 700.0},
            "price_per_person": {"currency": "USD", "amount": 700.0},
            "scores": {},
            "booking_url": "https://book.aa.com/f3",
            "provider": "American Airlines",
            "available": True
        },
        {
            "id": "f4",
            "outbound": {
                "origin": {"city": "New York", "country": "USA", "airport_code": "JFK", "latitude": 40.6413, "longitude": -73.7781},
                "destination": {"city": "London", "country": "UK", "airport_code": "LHR", "latitude": 51.4700, "longitude": -0.4543},
                "departure_time": "2025-12-20T12:30:00",
                "arrival_time": "2025-12-20T23:45:00",
                "duration_minutes": 735,
                "stops": 1,
                "layovers": [{"airport": {"city": "Reykjavik", "country": "Iceland", "airport_code": "KEF", "latitude": 63.9850, "longitude": -22.6056}, "duration_minutes": 75}],
                "airline": "Icelandair",
                "flight_number": "FI404",
                "aircraft": "B757",
                "cabin_class": "economy",
                "amenities": {"wifi": True, "meal": True, "entertainment": False, "power_outlet": False, "legroom_inches": 31}
            },
            "return": None,
            "total_price": {"currency": "USD", "amount": 600.0},
            "price_per_person": {"currency": "USD", "amount": 600.0},
            "scores": {},
            "booking_url": "https://book.icelandair.com/f4",
            "provider": "Icelandair",
            "available": True
        },
        {
            "id": "f5",
            "outbound": {
                "origin": {"city": "New York", "country": "USA", "airport_code": "JFK", "latitude": 40.6413, "longitude": -73.7781},
                "destination": {"city": "London", "country": "UK", "airport_code": "LHR", "latitude": 51.4700, "longitude": -0.4543},
                "departure_time": "2025-12-20T14:00:00",
                "arrival_time": "2025-12-20T22:00:00",
                "duration_minutes": 480,
                "stops": 0,
                "layovers": [],
                "airline": "United Airlines",
                "flight_number": "UA908",
                "aircraft": "B787",
                "cabin_class": "business",
                "amenities": {"wifi": True, "meal": True, "entertainment": True, "power_outlet": True, "legroom_inches": 36}
            },
            "return": None,
            "total_price": {"currency": "USD", "amount": 950.0},
            "price_per_person": {"currency": "USD", "amount": 950.0},
            "scores": {},
            "booking_url": "https://book.united.com/f5",
            "provider": "United Airlines",
            "available": True
        },
        {
            "id": "f6",
            "outbound": {
                "origin": {"city": "New York", "country": "USA", "airport_code": "JFK", "latitude": 40.6413, "longitude": -73.7781},
                "destination": {"city": "London", "country": "UK", "airport_code": "LHR", "latitude": 51.4700, "longitude": -0.4543},
                "departure_time": "2025-12-20T15:30:00",
                "arrival_time": "2025-12-20T23:30:00",
                "duration_minutes": 480,
                "stops": 0,
                "layovers": [],
                "airline": "Virgin Atlantic",
                "flight_number": "VS12",
                "aircraft": "A330",
                "cabin_class": "economy",
                "amenities": {"wifi": True, "meal": True, "entertainment": True, "power_outlet": True, "legroom_inches": 31}
            },
            "return": None,
            "total_price": {"currency": "USD", "amount": 640.0},
            "price_per_person": {"currency": "USD", "amount": 640.0},
            "scores": {},
            "booking_url": "https://book.virginatlantic.com/f6",
            "provider": "Virgin Atlantic",
            "available": True
        },
        {
            "id": "f7",
            "outbound": {
                "origin": {"city": "New York", "country": "USA", "airport_code": "JFK", "latitude": 40.6413, "longitude": -73.7781},
                "destination": {"city": "London", "country": "UK", "airport_code": "LHR", "latitude": 51.4700, "longitude": -0.4543},
                "departure_time": "2025-12-20T17:00:00",
                "arrival_time": "2025-12-21T05:00:00",
                "duration_minutes": 720,
                "stops": 0,
                "layovers": [],
                "airline": "American Airlines",
                "flight_number": "AA102",
                "aircraft": "B777",
                "cabin_class": "economy",
                "amenities": {"wifi": True, "meal": True, "entertainment": True, "power_outlet": True, "legroom_inches": 31}
            },
            "return": None,
            "total_price": {"currency": "USD", "amount": 670.0},
            "price_per_person": {"currency": "USD", "amount": 670.0},
            "scores": {},
            "booking_url": "https://book.aa.com/f7",
            "provider": "American Airlines",
            "available": True
        }
    ]
}
