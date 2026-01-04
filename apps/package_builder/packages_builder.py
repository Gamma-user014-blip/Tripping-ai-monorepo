# compare.py
from haversine import haversine, Unit
import numpy as np
from score_algorithms import *


def build_package(packet):

    entry_flights = packet["entry_flights"]
    list_of_hotels = packet["list_of_hotels"]
    exit_flights = packet["exit_flights"]


    entry_flight = get_best_flight(entry_flights)
    list_of_chosen_hotels = [get_best_hotel(hotels) for hotels in list_of_hotels]
    exit_flight = get_best_flight(exit_flights)

    entry_flight["type"] = "flight"
    for hotel in list_of_chosen_hotels:
        hotel["type"] = "hotel"

    exit_flight["type"] = "flight"
    package = [entry_flight] + list_of_chosen_hotels + [exit_flight]
    

    return package
    

    




def flights_to_airport(flights, closest_airport_code):
    """
    Returns flights that arrive at the specified airport (checks outbound.destination.airport_code)
    """
    result = []
    for flight in flights:
        outbound = flight.get("outbound")
        if outbound and outbound["destination"]["airport_code"] == closest_airport_code:
            result.append(flight)
    return result

def add_cheapest_flight(pairs):
    """
    Adds 'cheapest_flight' field to each hotel-airport pair
    """
    for pair in pairs:
        if pair.get("flights"):
            # Sort by price in USD to get the cheapest
            flights_sorted = sorted(
                pair["flights"],
                key=lambda f: f["price_per_person"]["amount"]  # or convert to USD if needed
            )
            pair["cheapest_flight"] = flights_sorted[0]

def find_closest_airports(hotels, airport_list, flights):
    """
    Pairs every hotel with its closest airport and relevant flights
    Returns list of dicts: {"hotel": hotel, "closest_airport": code, "distance_km": float, "flights": [...]}
    """
    # Extract coordinates
    airport_coords = np.array([[airport["lat"], airport["lon"]] for airport in airport_list])
    airport_codes = [airport["code"] for airport in airport_list]

    results = []
    for hotel in hotels:
        hotel_loc = hotel["location"]
        hotel_coord = np.array([hotel_loc["latitude"], hotel_loc["longitude"]])
        distances = np.array([
            haversine(hotel_coord, airport_coord, unit=Unit.KILOMETERS)
            for airport_coord in airport_coords
        ])
        idx_min = np.argmin(distances)
        results.append({
            "hotel": hotel,
            "closest_airport": airport_codes[idx_min],
            "distance_km": distances[idx_min],
            "flights": []
        })

    # Match flights with hotel-airport
    for pair in results[:]:
        closest_airport = pair["closest_airport"]
        relevant_flights = flights_to_airport(flights, closest_airport)

        # Sort flights by price (converted to USD)
        for f in relevant_flights:
            currency = f["price_per_person"]["currency"]
            f["price_usd"] = f["price_per_person"]["amount"] * {
                "USD": 1.0, "EUR": 1.084, "GBP": 1.27, "ILS": 0.27
            }.get(currency, 1.0)

        relevant_flights_sorted = sorted(relevant_flights, key=lambda f: f["price_usd"])

        if not relevant_flights_sorted:
            results.remove(pair)
        else:
            pair["flights"] = relevant_flights_sorted

    return results
