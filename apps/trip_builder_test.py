import requests
import json
import time

# Trip Builder is on port 8100 in docker-compose.yml (exposed 8100:8000)
# But wait, looking at docker-compose.yml:
# hotel_retriever: 8001:8000
# trip_builder: 8100:8000
# package_builder: 8200:8000
TRIP_BUILDER_URL = "http://localhost:8100"

def test_full_trip_flow():
    print(f"Testing Full Trip Flow at {TRIP_BUILDER_URL}...")
    
    # Construct a full trip request
    payload = {
        "user_id": "test_user_123",
        "sections": [
            {
                "type": "stay",
                "data": {
                    "hotel_request": {
                        "location": {"city": "New York", "country": "US"},
                        "dates": {"start_date": "2025-09-01", "end_date": "2025-09-05"},
                        "guests": 2,
                        "rooms": 1,
                        "preferences": [],
                        "max_results": 10,
                        "max_price_per_night": 2000.0,
                        "min_rating": 0
                    },
                    "activity_request": {
                        "location": {"city": "New York", "country": "US"},
                        "dates": {"start_date": "2025-09-01", "end_date": "2025-09-05"},
                        "preferences": [],
                        "max_results": 5
                    }
                }
            }
        ]
    }

    try:
        print("Sending request to /api/create_trip (this may take a while)...")
        start_time = time.time()
        response = requests.post(
            f"{TRIP_BUILDER_URL}/api/create_trip", 
            json=payload, 
            timeout=120
        )
        duration = time.time() - start_time
        
        print(f"Status: {response.status_code} (took {duration:.2f}s)")
        
        if response.status_code != 200:
            print("Error details:", response.text)
            return

        package = response.json()
        sections = package.get("sections", [])
        print(f"Package received with {len(sections)} sections.")

        found_hotel_with_image = False
        for section in sections:
            if section.get("type") == "stay":
                hotel = section.get("data", {}).get("hotel", {})
                name = hotel.get("name", "Unknown Hotel")
                image = hotel.get("image", "")
                
                print(f"Selected Hotel: {name}")
                print(f"Image URL: {image if image else 'MISSING'}")
                
                if image:
                    found_hotel_with_image = True
                else:
                    print("FAIL: Hotel image is missing in the final package!")

        if found_hotel_with_image:
            print("\nSUCCESS: End-to-end flow verified. Images are correctly injected into the final package!")
        else:
            print("\nVERIFICATION FAILED: No hotels with images found in the response.")

    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {TRIP_BUILDER_URL}. Ensure all services (hotel_retriever, trip_builder, package_builder) are running in Docker.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_full_trip_flow()
