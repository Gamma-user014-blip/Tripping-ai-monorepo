import requests
import json
import data_loader
import time

# Packet data
packet = data_loader.get_full_packet()

URL = "http://127.0.0.1:81/build-package"

def run_client():
    try:
        print(f"Sending request to {URL}...")
        start_time = time.time()
        
        response = requests.post(URL, json=packet)
        response.raise_for_status()
        
        end_time = time.time()
        print(f"Request completed in {(end_time - start_time) * 1000:.2f} ms")
        
        result = response.json()
        
        if isinstance(result, list):
            print(f"Package length: {len(result)}")
            # Item types are now injected by the builder based on stage type
            types = [item.get("type") for item in result]
            print(f"Item types: {types}")
            for item in result:
                score = item.get("scores", {}).get("preference_score", "N/A")
                print(f" - {item.get('type', '???')} ({item['id']}): {score}")
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
