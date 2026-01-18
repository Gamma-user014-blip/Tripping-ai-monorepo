from datetime import datetime
from typing import List
from .currency_service import get_currency_rate
from shared.data_types.models import FlightOption, HotelOption, ComponentScores, FlightSegment, ActivityOption
from collections import defaultdict



TIME_NAMES = {
        "morning": (6, 9),   # 6:00–9:59
        "morning_late": (9, 12),   # 9:00–11:59
        "afternoon": (12, 14.5), # 12:00–14:59
        "afternoon_late": (14.5, 17), # 14:59–17:59
        "evening": (17, 19),  # 17:00–19:59
        "evening_late": (19, 21),  # 19:59–21:59
        "night": (21, 6),      # 21:00–5:59
}


def set_flights_scores(flights: List[FlightOption]):
    for flight in flights:
        set_flight_scores(flight)

def set_hotels_scores(hotels: List[HotelOption]):
    for hotel in hotels:
        set_hotel_scores(hotel)  


def get_best_activities(activities: List[ActivityOption]):
    set_activities_scores(activities)
    times = split_activities_by_time(activities)
    best_activities = best_per_bucket(times)
    return list(best_activities.values())


def best_per_bucket(times):
    best_activities = {}
    for time_name, acts in times.items():
        if acts:
            # pick activity with highest preference_score
            best_activities[time_name] = max(acts, key=lambda activity: activity.scores.preference_score)
    return best_activities


def split_activities_by_time(activities):
    times = defaultdict(list)

    for act in activities:
        for slot in act.available_times:
            # parse time "HH:MM"
            slot = slot.time
            hour = int(slot.split(":")[0])
            
            # assign to bucket
            for time_name, (start, end) in TIME_NAMES.items():
                if start <= end:
                    if start <= hour < end:
                        times[time_name].append(act)
                else:
                    # wrap-around case for night (21–6)
                    if hour >= start or hour < end:
                        times[time_name].append(act)
    return times

def set_activities_scores(activities: List[ActivityOption]):
    for activity in activities:
        set_activity_scores(activity)


def set_activity_scores(activity: ActivityOption):

    max_price = 1000  # for normalization
    price = get_currency_rate(activity.price_per_person.currency) * activity.price_per_person.amount
    relative_price = price / max(activity.duration_minutes, 1)  # avoid division by zero
    
    # Invert price so cheaper per minute -> higher score
    inverted_price = max(0, max_price - relative_price)
    
    # Weight rating factor based on review count
    if activity.review_count > 20:
        rating_factor = 0.7
    else:
        rating_factor = 0.5
    
    preference_score = activity.rating * rating_factor + (inverted_price / max_price) * (1 - rating_factor)
    price_score = (inverted_price / max_price) * 0.7 + activity.rating * 0.3
    
    activity.scores = ComponentScores(
        price_score=price_score,
        quality_score=0,
        convenience_score=0,
        preference_score=preference_score
    )



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
