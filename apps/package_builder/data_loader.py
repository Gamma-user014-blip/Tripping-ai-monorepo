# data_loader.py
from .sample import *
from shared.data_types.models import (
    TripResponse, TripSectionResponse, SectionType, 
    FlightResponse, StayResponse, FlightOption, HotelOption, ActivityOption
)

def get_full_packet() -> TripResponse:
    """
    Returns a TripResponse object populated with sample data.
    """
    # Helper to fix 'return': None in sample data which fails FlightOption validation
    def clean_flight(f):
        f_copy = f.copy()
        if f_copy.get("return") is None:
            f_copy.pop("return", None)
        return f_copy

    sections = [
        TripSectionResponse(
            type=SectionType.FLIGHT,
            data=FlightResponse(options=[FlightOption(**clean_flight(f)) for f in get_flights()])
        ),
        TripSectionResponse(
            type=SectionType.STAY,
            data=StayResponse(
                hotel_options=[HotelOption(**h) for h in get_hotels()],
                activity_options=[ActivityOption(**a) for a in get_activities() if a['location']['city'] == 'London']
            )
        ),
        TripSectionResponse(
            type=SectionType.STAY,
            data=StayResponse(
                hotel_options=[HotelOption(**h) for h in get_hotels2()],
                activity_options=[ActivityOption(**a) for a in get_activities() if a['location']['city'] == 'Manchester']
            )
        ),
        TripSectionResponse(
            type=SectionType.FLIGHT,
            data=FlightResponse(options=[FlightOption(**clean_flight(f)) for f in get_flights2()])
        )
    ]
    return TripResponse(sections=sections)

def get_hotels(): return hotels_packet["options"]
def get_hotels2(): return hotels_packet2["options"]
