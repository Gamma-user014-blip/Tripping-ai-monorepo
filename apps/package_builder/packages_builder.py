from .score_algorithms import *
from shared.data_types.models import (
    TripResponse, SectionType, FlightResponse, StayResponse, TransferResponse,
    FinalTripLayout, FinalTripSection, FinalStayOption
)

def build_package(trip: TripResponse) -> FinalTripLayout:
    """
    Builds a package by selecting the best item from each section.
    Returns a FinalTripLayout object.
    """
    layout = FinalTripLayout(sections=[])

    for section in trip.sections:
        if section.type == SectionType.FLIGHT:
            data = section.data
            if isinstance(data, FlightResponse) and data.options:
                best_flight = get_best_flight(data.options)
                if best_flight:
                    layout.sections.append(
                        FinalTripSection(type=SectionType.FLIGHT, data=best_flight)
                    )
                    
        elif section.type == SectionType.STAY:
            data = section.data
            if isinstance(data, StayResponse):
                stay_option = FinalStayOption()
                
                if data.hotel_options:
                    best_hotel = get_best_hotel(data.hotel_options)
                    if best_hotel:
                        stay_option.hotel = best_hotel
                
                if data.activity_options:
                    # Activities scoring implemented simple head for now
                    stay_option.activity = [data.activity_options[0]]
                
                layout.sections.append(
                    FinalTripSection(type=SectionType.STAY, data=stay_option)
                )
                    
        elif section.type == SectionType.TRANSFER:
            data = section.data
            if isinstance(data, TransferResponse) and data.options:
                # Transfer scoring to be implemented
                layout.sections.append(
                    FinalTripSection(type=SectionType.TRANSFER, data=data.options[0])
                )

    return layout
