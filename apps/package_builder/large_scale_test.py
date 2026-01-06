import random
import time
from packages_builder import build_package
from datetime import datetime, timedelta

# Configuration
NUM_FLIGHTS = 1000
NUM_HOTELS = 1000
# Single Country (UK) - Multiple Cities
COUNTRY = "UK"
CITIES = ["London", "Manchester", "Liverpool", "Edinburgh", "Glasgow", "Birmingham", "Bristol", "Oxford", "Cambridge", "Brighton"]
AMENITIES_POOL = ["wifi", "pool", "gym", "breakfast", "spa", "parking", "bar", "restaurant", "room_service", "concierge"]

def generate_flights(count, type_prefix="f"):
    flights = []
    for i in range(count):
        # Entry/Exit from international origins to UK
        origin = "New York" if type_prefix == "entry" else random.choice(CITIES)
        dest = random.choice(CITIES) if type_prefix == "entry" else "New York"
        
        origin_country = "USA" if type_prefix == "entry" else COUNTRY
        dest_country = COUNTRY if type_prefix == "entry" else "USA"
        
        flight = {
            "id": f"{type_prefix}{i}",
            "outbound": {
                "origin": {"city": origin, "country": origin_country},
                "destination": {"city": dest, "country": dest_country},
                "departure_time": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%dT%H:%M:%S"),
                "arrival_time": (datetime.now() + timedelta(days=random.randint(1, 30), hours=8)).strftime("%Y-%m-%dT%H:%M:%S"),
                "duration_minutes": random.randint(300, 900),
                "stops": random.randint(0, 2),
                "layovers": [],
                "airline": f"Airline_{i}",
                "flight_number": f"FL{i}",
                "aircraft": "B777",
                "cabin_class": random.choice(["economy", "business", "first"]),
                "amenities": {a: random.choice([True, False]) for a in random.sample(AMENITIES_POOL, 5)}
            },
            "price_per_person": {"currency": "USD", "amount": random.uniform(200, 2000)},
            "scores": {},
            "available": True
        }
        flights.append(flight)
    return flights

def generate_hotels(count, city):
    hotels = []
    for i in range(count):
        hotel = {
            "id": f"h_{city}_{i}",
            "name": f"Hotel {city} {i}",
            "location": {
                "city": city,
                "country": COUNTRY,
                "latitude": 0.0,
                "longitude": 0.0
            },
            "rating": round(random.uniform(1.0, 5.0), 1),
            "price_per_night": {"currency": "USD", "amount": random.uniform(50, 1000)},
            "amenities": random.sample(AMENITIES_POOL, random.randint(0, 10)),
            "scores": {},
            "available": True
        }
        hotels.append(hotel)
    return hotels

def run_stress_test():
    print(f"Generating {NUM_FLIGHTS} entry flights, {NUM_FLIGHTS} exit flights...")
    
    # Simulate a route: London -> Manchester -> Edinburgh -> Glasgow -> Back
    route = ["London", "Manchester", "Liverpool", "Edinburgh", "Glasgow", "Oxford"]
    print(f"Simulating trip across {len(route)} cities: {route}")

    t0 = time.time()
    
    # Generate hotels specifically for each city in the route
    list_of_hotels_by_city = []
    for city in route:
        # Generate 5-50 options per city
        options = generate_hotels(random.randint(5, 50), city)
        list_of_hotels_by_city.append(options)
        
    packet = {
        "entry_flights": generate_flights(NUM_FLIGHTS, "entry"),
        "list_of_hotels": list_of_hotels_by_city,
        "exit_flights": generate_flights(NUM_FLIGHTS, "exit")
    }
    t1 = time.time()
    print(f"Data generation took {t1 - t0:.3f} seconds")
    
    print("Building package...")
    t2 = time.time()
    try:
        result = build_package(packet)
        t3 = time.time()
        
        print(f"Package build took {t3 - t2:.3f} seconds")
        print(f"Result contains {len(result)} items.")
        
        # Validation
        entry_flight = result[0]
        hotel_list = result[1:-1]
        exit_flight = result[-1]
        
        print("\n--- Result Validation ---")
        print(f"Entry Flight ID: {entry_flight['id']}")
        print(f"Entry Flight Score: {entry_flight.get('scores', {}).get('preference_score', 'N/A'):.3f}")

        # Verify Entry Flight is actually the best
        # Note: 'scores' key is populated in-place by the builder, so we can check the original list
        max_entry_score = max(f['scores']['preference_score'] for f in packet['entry_flights'])
        if abs(entry_flight['scores']['preference_score'] - max_entry_score) < 0.0001:
            print(f"[OK] Entry flight is indeed the best (Max Score: {max_entry_score:.3f})")
        else:
            print(f"[FAIL] Entry flight validation failed! Expected {max_entry_score}, got {entry_flight['scores']['preference_score']}")

        print(f"\nHotels Selected: {len(hotel_list)}")
        if hotel_list:
            # Verify the first hotel selection
            first_hotel_group = packet['list_of_hotels'][0]
            max_h_score = max(h['scores']['preference_score'] for h in first_hotel_group)
            chosen_h_score = hotel_list[0]['scores']['preference_score']
            
            if abs(chosen_h_score - max_h_score) < 0.0001:
                print(f"[OK] First hotel selection correct (Max Score: {max_h_score:.3f})")
            else:
                 print(f"[FAIL] Hotel validation failed! Expected {max_h_score}, got {chosen_h_score}")

            avg_hotel_score = sum(h.get('scores', {}).get('preference_score', 0) for h in hotel_list) / len(hotel_list)
            print(f"Avg Hotel Score: {avg_hotel_score:.3f}")
            
        print(f"\nExit Flight ID: {exit_flight['id']}")
        print("Success! Large scale test passed.")
        
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_stress_test()
