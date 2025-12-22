# main.py
from data_loader import get_hotels, get_flights, build_airport_list
from compare import find_closest_airports

def flights_to_closest_airport(hotel, flights, closest_airport_code):
    """
    Returns all flights arriving at the closest airport for a hotel.
    """
    return [
        flight for flight in flights
        if flight["route"]["to_airport"] == closest_airport_code
    ]

def main():
    hotels = get_hotels()
    flights = get_flights()
    airport_list = build_airport_list(flights)

    closest_airports = find_closest_airports(hotels, airport_list)

    for item in closest_airports:
        hotel_name = item["hotel_name"]
        hotel_city = item["hotel_city"]
        closest_airport = item["closest_airport"]
        distance = item["distance_km"]

        relevant_flights = flights_to_closest_airport(item, flights, closest_airport)

        print(f"\n{hotel_name} ({hotel_city}) -> Closest Airport: {closest_airport}, Distance: {distance:.2f} km")
        if relevant_flights:
            for flight in relevant_flights:
                print(f"  - {flight["route"]['airline']} from {flight['route']['from_airport']} to {flight['route']['to_airport']}, "
                      f"Price: {flight['price']} {flight['currency']}, Connections: {flight['connections']}")
        else:
            print("  - No flights available to this airport.")

if __name__ == "__main__":
    main()
