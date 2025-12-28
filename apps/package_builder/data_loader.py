# data_loader.py
from sample import hotels_packet, flights_packet
import json
def get_hotels():
    """
    Returns the list of hotels from the packet
    """

    #return json.loads(hotels_packet)
    return hotels_packet["hotels"]

def get_flights():
    """
    Returns the list of flights from the packet
    """
    return flights_packet["flights"]

def build_airport_list(flights):
    """
    Extracts unique airports (from & to) and returns a list of dicts with lat/lon.
    """
    airport_list = []
    seen_airports = set()
    for flight in flights:
        route = flight["route"]
        for code, lat, lon in [
            (route["from_airport"], route["from_latitude"], route["from_longitude"]),
            (route["to_airport"], route["to_latitude"], route["to_longitude"])
        ]:
            if code not in seen_airports:
                airport_list.append({"code": code, "lat": lat, "lon": lon})
                seen_airports.add(code)
    return airport_list
