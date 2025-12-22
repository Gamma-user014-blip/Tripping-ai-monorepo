# compare.py
from haversine import haversine, Unit
import numpy as np



def flights_to_closest_airport(flights, closest_airport_code):
    """
    Returns all flights arriving at the closest airport for a hotel.
    """
    return [
        flight for flight in flights
        if flight["route"]["to_airport"] == closest_airport_code
    ]



def add_cheapest_flight(pairs):
    for pair in pairs:
        pair["cheapest_flight"] = pair["flights"][0]

def find_closest_airports(hotels, airport_list, flights):
    """
    Vectorized computation: returns list of dicts with closest airport info.
    """
    airport_coords = np.array([[a["lat"], a["lon"]] for a in airport_list])
    airport_codes = [a["code"] for a in airport_list]

    results = []
    for hotel in hotels:
        hotel_coord = np.array([hotel["latitude"], hotel["longitude"]])
        distances = np.array([
            haversine(hotel_coord, airport_coord, unit=Unit.KILOMETERS)
            for airport_coord in airport_coords
        ])
        idx_min = np.argmin(distances)
        results.append({
            "hotel": hotel,
            "closest_airport": airport_codes[idx_min],
            "distance_km": distances[idx_min],
            "flight": {}
        })

    for pair in results[:]:
        closest_airport = pair["closest_airport"]

        relevant_flights = sorted(flights_to_closest_airport(flights, closest_airport), key=lambda flight: flight["price"])

        if not relevant_flights:
            results.remove(pair)
        else:
            pair["flights"] = relevant_flights
    return results
