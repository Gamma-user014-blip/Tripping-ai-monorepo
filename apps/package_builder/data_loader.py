# data_loader.py
from sample import *

def get_full_packet():
    """
    Returns a packet as a list of stage dictionaries matching the sample structure.
    """
    return [
        {"type": "flight", "options": get_flights()},
        {"type": "hotel", "options": get_hotels()},
        {"type": "hotel", "options": get_hotels2()},
        {"type": "flight", "options": get_flights2()}
    ]

def get_hotels(): return hotels_packet["options"]
def get_hotels2(): return hotels_packet2["options"]
def get_flights2(): return flights_packet2["options"]
def get_flights(): return flights_packet["options"]
