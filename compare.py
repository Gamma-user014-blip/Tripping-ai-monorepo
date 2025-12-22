# compare.py
from haversine import haversine, Unit
import numpy as np

def find_closest_airports(hotels, airport_list):
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
            "hotel_name": hotel["name"],
            "hotel_city": hotel["city"],
            "closest_airport": airport_codes[idx_min],
            "distance_km": distances[idx_min]
        })
    return results
