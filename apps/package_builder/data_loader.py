# data_loader.py
from sample import hotels_packet, flights_packet

def get_hotels():
    """
    Returns the list of hotels from the packet (proto-compliant format)
    """
    return hotels_packet["options"]

def get_flights():
    """
    Returns the list of flights from the packet (proto-compliant format)
    """
    return flights_packet["options"]

def build_airport_list(flights):
    """
    Extracts unique airports (from & to) from flights and returns a list of dicts:
    [{"code": IATA, "lat": latitude, "lon": longitude}, ...]
    Works with proto-compliant FlightSegment objects.
    """
    airport_list = []
    seen_airports = set()

    for flight in flights:
        for segment_key in ["outbound", "return"]:
            segment = flight.get(segment_key)
            if not segment:
                continue
            origin = segment["origin"]
            dest = segment["destination"]

            for loc in [origin, dest]:
                code = loc.get("airport_code")
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                if code and code not in seen_airports:
                    airport_list.append({"code": code, "lat": lat, "lon": lon})
                    seen_airports.add(code)

    return airport_list
