from score_algorithms import *
from shared.data_types.models import TripResponse, SectionType, FlightResponse, StayResponse, TransferResponse

def build_package(trip: TripResponse):
    """
    Builds a package by selecting the best item from each section.
    'trip' is a TripResponse object containing multiple sections.
    """
    selected_items = []

    for section in trip.sections:
        if section.type == SectionType.FLIGHT:
            data = section.data
            if isinstance(data, FlightResponse) and data.options:
                best_flight = get_best_flight(data.options)
                if best_flight:
                    selected_items.append(best_flight)
                    
        elif section.type == SectionType.STAY:
            data = section.data
            if isinstance(data, StayResponse):
                if data.hotel_options:
                    best_hotel = get_best_hotel(data.hotel_options)
                    if best_hotel:
                        selected_items.append(best_hotel)
                
                if data.activity_options:
                    # Activities scoring implemented simple head for now
                    selected_items.append(data.activity_options[0])
                    
        elif section.type == SectionType.TRANSFER:
            data = section.data
            if isinstance(data, TransferResponse) and data.options:
                # Transfer scoring to be implemented
                selected_items.append(data.options[0])

    return selected_items
