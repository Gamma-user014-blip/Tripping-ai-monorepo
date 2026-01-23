import sys
import os
import requests
import json
from .data_loader import *
import time

# Packet data
packet = get_full_packet()

URL = "http://127.0.0.1:8100/api/build-package"

def run_client():
    try:
        print(f"Sending request to {URL}...")
        start_time = time.time()
        
        # requests doesn't handle Pydantic models, so we dump to dict first
        response = requests.post(URL, json=packet.model_dump())
        response.raise_for_status()
        
        end_time = time.time()
        print(f"Request completed in {(end_time - start_time) * 1000:.2f} ms")
        
        result = response.json()
        
        if isinstance(result, dict) and "sections" in result:
            sections = result["sections"]
            print(f"Package length: {len(sections)}")
            for item in sections:
                item_type = item['type']
                data = item['data']
                if item_type == "stay":
                    hotel_id = data.get('hotel', {}).get('id', 'N/A')
                    activity_count = len(data.get('activities', []))
                    print(f"{item_type}: Hotel {hotel_id}, Activities: {activity_count}")
                    for activity in data.get('activities', []):
                        print(f"{activity["name"]}")
                else:
                    print(f"{item_type}: {data.get('id', 'N/A')}")
            print("Success! Package received.")
        else:
            print("Received unexpected response struct:")
            print(result)

    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to {URL}. Is the API running?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_client()
