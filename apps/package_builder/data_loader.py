# data_loader.py
from sample import *



def get_full_packet():
    packet = {
        "entry_flights" : get_flights(),
        "list_of_hotels":
        [
            get_hotels(), get_hotels2()
        ],
        "exit_flights" : get_flights2()
    }
    
    return packet

def get_hotels():
    """
    Returns the list of hotels from the packet (proto-compliant format)
    """
    return hotels_packet["options"]

def get_hotels2():
    """
    Returns the list of hotels from the packet (proto-compliant format)
    """
    return hotels_packet2["options"]

def get_flights2():
    return flights_packet2["options"]

def get_flights():
    """
    Returns the list of flights from the packet (proto-compliant format)
    """
    return flights_packet["options"]




