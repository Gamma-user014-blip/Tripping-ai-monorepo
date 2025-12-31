# main.py
from data_loader import get_hotels, get_flights, build_airport_list
from packages_builder import find_closest_airports, add_cheapest_flight
from score_algorithms import *
def main():
    hotels = get_hotels()
    set_hotels_scores(hotels)
    print(get_best_hotel(hotels))
    flights = get_flights()
    set_flights_scores(flights)
    print(get_best_flight(flights))
    airport_list = build_airport_list(flights)

    # Pair hotels with closest airport and flights
    hotel_airport_pairs = find_closest_airports(hotels, airport_list, flights) 

    # Sort by hotel rating

    # Add the cheapest flight for each hotel-airport pair
    add_cheapest_flight(hotel_airport_pairs)

    give_packages_scores(hotel_airport_pairs)
    sorted_pairs = sorted(hotel_airport_pairs, key=lambda pair: pair["scores"]["normal"], reverse=True)

    # Print results
    for pair in sorted_pairs:
        hotel = pair["hotel"]
        flight = pair.get("cheapest_flight")
        if flight:
            airline = flight["outbound"]["airline"]
        else:
            airline = "N/A"
        print(hotel["name"], hotel["rating"], airline)
    print("\n")







if __name__ == "__main__":
    main()
