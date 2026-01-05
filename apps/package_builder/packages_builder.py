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
