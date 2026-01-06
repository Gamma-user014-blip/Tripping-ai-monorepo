import random
import time
import requests
from datetime import datetime, timedelta

# Configuration
URL = "http://127.0.0.1:81/build-package"
NUM_FLIGHTS = 1000
NUM_HOTELS = 1000
COUNTRY = "UK"
CITIES = ["London", "Manchester", "Liverpool", "Edinburgh", "Glasgow"]
AMENITIES_POOL = ["wifi", "pool", "gym", "breakfast", "spa"]

def generate_flights(count, type_prefix="f"):
    flights = []
    for i in range(count):
        origin = "New York" if type_prefix == "entry" else random.choice(CITIES)
        dest = random.choice(CITIES) if type_prefix == "entry" else "New York"
        flights.append({
            "id": f"{type_prefix}{i}",
            "outbound": {
                "origin": {"city": origin, "country": "USA" if type_prefix == "entry" else COUNTRY},
                "destination": {"city": dest, "country": COUNTRY if type_prefix == "entry" else "USA"},
                "departure_time": "2026-06-01T10:00:00",
                "arrival_time": "2026-06-01T18:00:00",
                "duration_minutes": random.randint(300, 900),
                "stops": random.randint(0, 2),
                "airline": "Airline_Flight",
                "flight_number": f"FL{i}"
            },
            "price_per_person": {"currency": "USD", "amount": random.uniform(200, 2000)},
            "available": True
        })
    return flights

def generate_hotels(count, city):
    hotels = []
    for i in range(count):
        hotels.append({
            "id": f"h_{city}_{i}",
            "name": f"Hotel {city} {i}",
            "location": {"city": city, "country": COUNTRY},
            "rating": round(random.uniform(1.0, 5.0), 1),
            "price_per_night": {"currency": "USD", "amount": random.uniform(50, 1000)},
            "amenities": random.sample(AMENITIES_POOL, random.randint(0, 5)),
            "available": True
        })
    return hotels

def run_api_stress_test():
    print(f"--- API Large Scale Test ---")
    print(f"Generating large payload...")
    
    packet = [
        {"type": "flight", "options": generate_flights(NUM_FLIGHTS, "entry")},
        {"type": "hotel", "options": generate_hotels(NUM_HOTELS, "London")},
        {"type": "hotel", "options": generate_hotels(NUM_HOTELS, "Manchester")},
        {"type": "flight", "options": generate_flights(NUM_FLIGHTS, "exit")}
    ]

    print(f"Sending request to {URL}...")
    try:
        t0 = time.time()
        response = requests.post(URL, json=packet)
        t1 = time.time()
        
        response.raise_for_status()
        result = response.json()
        
        print(f"API Response Time: {t1 - t0:.3f} seconds")
        print(f"Package Size: {len(result)} items")
        
        for i, item in enumerate(result):
            score = item.get("scores", {}).get("preference_score", "N/A")
            print(f" Stage {i}: {item.get('type', '???')} ({item['id']}) - Score: {score}")

        print("\nSuccess! API handles large payloads correctly.")
    except Exception as e:
        print(f"Test Failed: {e}")
        print("Tip: Make sure the server is running (python main.py)")

if __name__ == "__main__":
    run_api_stress_test()
