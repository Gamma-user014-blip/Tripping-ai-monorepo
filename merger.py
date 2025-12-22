# main.py
from data_loader import get_hotels, get_flights, build_airport_list
from packages_builder import find_closest_airports, add_cheapest_flight



def main():
    hotels = get_hotels()
    flights = get_flights()
    airport_list = build_airport_list(flights)

    hotel_airport_pairs = find_closest_airports(hotels, airport_list, flights) 

    sorted_pairs = sorted(hotel_airport_pairs, key=lambda pair: pair["hotel"]["rating"], reverse=True)
    add_cheapest_flight(sorted_pairs)
    for pair in sorted_pairs:
       print(pair["hotel"]["name"], pair["hotel"]["rating"], pair["cheapest_flight"]["route"]["airline"])

if __name__ == "__main__":
    main()
