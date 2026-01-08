from datetime import datetime
from typing import List
from currency_service import get_currency_rate
from shared.data_types.models import FlightOption, HotelOption, ComponentScores, FlightSegment




def set_flights_scores(flights: List[FlightOption]):
    for flight in flights:
        set_flight_scores(flight)

def set_hotels_scores(hotels: List[HotelOption]):
    for hotel in hotels:
        set_hotel_scores(hotel)  

def get_best_flight(flights: List[FlightOption]):
    if not flights:
        return None
    if flights[0].scores.preference_score == 0.0:
        set_flights_scores(flights)
    return max(flights, key=lambda flight: flight.scores.preference_score)


def get_best_hotel(hotels: List[HotelOption]):
    if not hotels:
        return None
    if hotels[0].scores.preference_score == 0.0:
        set_hotels_scores(hotels)
    return max(hotels, key=lambda hotel: hotel.scores.preference_score)


def set_flight_scores(flight: FlightOption):
    outbound = flight.outbound
    flight_time = get_flight_time(outbound)  # in minutes
    connections = outbound.stops
    price = get_flight_price_usd(flight)

    flight.scores = ComponentScores(
        price_score=calc_flight_score(flight_time, connections, price, mode="budget"),
        quality_score=0,          # can be extended
        convenience_score=0,      # can be extended
        preference_score=calc_flight_score(flight_time, connections, price, mode="normal")
    )


def set_hotel_scores(hotel: HotelOption):
    """Compute hotel scores based on rating, price, amenities."""
    rating = hotel.rating
    price_per_night = get_hotel_price_usd(hotel)
    amenities_count = min(len(hotel.amenities), 10)

    hotel.scores = ComponentScores(
        price_score=calc_hotel_score(rating, price_per_night, amenities_count, mode="budget"),
        quality_score=0,         # can be extended
        convenience_score=0,     # can be extended
        preference_score=calc_hotel_score(rating, price_per_night, amenities_count, mode="normal")
    )


def calc_hotel_score(rating, price_per_night, amenities_count, mode="normal"):
    """Normalized 0-1 hotel score."""
    ref_price = 1500
    ref_rating = 5
    ref_amenities = 10

    if mode == "normal":
        score = 0.5 * (rating / ref_rating) + 0.3 * (1 - price_per_night / ref_price) + 0.2 * (amenities_count / ref_amenities)
    elif mode == "budget":
        score = 0.3 * (rating / ref_rating) + 0.6 * (1 - price_per_night / ref_price) + 0.1 * (amenities_count / ref_amenities)

    return max(0, min(score, 1))


def calc_flight_score(flight_time, connections, price, mode="normal"):
    """Normalized 0-1 flight score."""
    ref_price = 1000
    ref_duration = 720
    ref_connections = 2

    if mode == "normal":
        raw = 0.5 * (price / ref_price) + 0.35 * (flight_time / ref_duration) + 0.15 * (connections / ref_connections)
    elif mode == "budget":
        raw = 0.7 * (price / ref_price) + 0.25 * (flight_time / ref_duration) + 0.05 * (connections / ref_connections)
    else:  # duration
        raw = 0.3 * (price / ref_price) + 0.65 * (flight_time / ref_duration) + 0.05 * (connections / ref_connections)

    return 1 - min(raw, 1)


def get_flight_time(segment: FlightSegment):
    if segment.duration_minutes > 0:
        return segment.duration_minutes

    # Use fromisoformat (up to 30x faster than strptime)
    try:
        dep = datetime.fromisoformat(segment.departure_time)
        arr = datetime.fromisoformat(segment.arrival_time)
        return (arr - dep).total_seconds() / 60
    except (ValueError, AttributeError):
        fmt = "%Y-%m-%dT%H:%M:%S"
        dep = datetime.strptime(segment.departure_time, fmt)
        arr = datetime.strptime(segment.arrival_time, fmt)
        return (arr - dep).total_seconds() / 60


def get_flight_price_usd(flight: FlightOption):
    """Convert flight price_per_person to USD."""
    price = flight.price_per_person.amount
    currency = flight.price_per_person.currency
    return get_currency_rate(currency) * price


def get_hotel_price_usd(hotel: HotelOption):
    """Convert hotel price_per_night to USD."""
    price = hotel.price_per_night.amount
    currency = hotel.price_per_night.currency
    return get_currency_rate(currency) * price
