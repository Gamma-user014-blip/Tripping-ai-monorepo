from .score_algorithms import *
from shared.data_types.models import (
    TripResponse, SectionType,
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
            # Use duck typing - check for options attribute directly
            options = getattr(data, 'options', None)
            if options:
                best_flight = get_best_flight(options)
                if best_flight:
                    layout.sections.append(
                        FinalTripSection(type=SectionType.FLIGHT, data=best_flight)
                    )
                    
        elif section.type == SectionType.STAY:
            data = section.data
            # Use duck typing - check for hotel_options attribute
            hotel_options = getattr(data, 'hotel_options', None)
            activity_options = getattr(data, 'activity_options', None)
            
            # Only create stay section if we have a valid hotel
            best_hotel = None
            if hotel_options:
                best_hotel = get_best_hotel(hotel_options)
            
            # Skip this stay section entirely if no hotel is available
            if not best_hotel or not best_hotel.id or not best_hotel.name:
                print(f"Skipping stay section - no valid hotel available")
                continue
            
            stay_option = FinalStayOption()
            stay_option.hotel = best_hotel
            
            if activity_options:
                # Activities scoring implemented simple head for now
                stay_option.activities = activity_options[:5]
            
            layout.sections.append(
                FinalTripSection(type=SectionType.STAY, data=stay_option)
            )
                    
        elif section.type == SectionType.TRANSFER:
            data = section.data
            # Use duck typing - check for options attribute
            options = getattr(data, 'options', None)
            if options:
                # Transfer scoring to be implemented
                layout.sections.append(
                    FinalTripSection(type=SectionType.TRANSFER, data=options[0])
                )

    return layout
