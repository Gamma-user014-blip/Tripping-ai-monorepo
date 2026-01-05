import socket
import json
import data_loader

# Flight mock data
flight_mock = {
    "price_per_person": {"amount": 500, "currency": "USD"},
    "outbound": {
        "departure_time": "2025-12-20T10:00:00",
        "arrival_time": "2025-12-20T14:00:00",
        "stops": 0
    }
    # Removed "scores": {} to ensure score calculation is triggered
}

# Hotel mock data
hotel_mock = {
    "rating": 4.5,
    "price_per_night": {"amount": 200, "currency": "USD"},
    "amenities": ["wifi", "pool"]
    # Removed "scores": {}
}

#packet = {
#    "entry_flights": [flight_mock],
#    "exit_flights": [flight_mock],
#    "list_of_hotels": [[hotel_mock]]  
#}

packet = data_loader.get_full_packet()

PORT = 1111
HOST = '127.0.0.1'

def run_client():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}")
            
            data = json.dumps(packet).encode('utf-8')
            s.sendall(data)
            s.shutdown(socket.SHUT_WR)
            
            response_data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response_data += chunk
            
            print("Received response:")
            try:
                decoded = json.loads(response_data.decode('utf-8'))
                if isinstance(decoded, list):
                    print(f"Package length: {len(decoded)}")
                    # Verify we have 3 items: flight, hotel, flight
                    types = [item.get("type") for item in decoded]
                    print(f"Item types: {types}")
                else:
                    print(decoded)
            except Exception as e:
                print(f"Failed to decode response: {e}")
                print(response_data)
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_client()
