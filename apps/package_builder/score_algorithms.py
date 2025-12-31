from datetime import datetime

EXCHANGE_RATES_TO_USD = {
    "USD": 1.0,
    "EUR": 1.084,
    "GBP": 1.27,
    "ILS": 0.27
}



def give_packages_scores(pairs):
    """Compute scores for all hotel-flight pairs."""
    for pair in pairs:
        set_package_score(pair)


def set_package_score(pair):
    # Hotel scores
    hotel = pair["hotel"]
    set_hotel_scores(hotel)
    hotel_scores = hotel["scores"]

    flights = pair["flights"]
    for flight in flights:
        set_flight_scores(flight)
    flights = sorted(flights, key=lambda flight: flight["scores"]["preference_score"], reverse=True)
    flight = flights[0]
    pair["cheapest_flight"] = flight


    # Flight scores
    if flight:
        flight_scores = flight["scores"]
    else:
        flight_scores = {"price_score": 0, "quality_score": 0, "convenience_score": 0, "preference_score": 0}

    # Distance between airport and hotel
    distance = pair.get("distance_km", 0)
    distance_score = 1 - min(distance / 50, 1)

    # Combined package scores
    pair["scores"] = {
        "normal": 0.4 * flight_scores.get("preference_score", 0) +
                  0.4 * hotel_scores.get("preference_score", 0) +
                  0.2 * distance_score,
        "budget": 0.4 * flight_scores.get("price_score", 0) +
                  0.4 * hotel_scores.get("price_score", 0) +
                  0.2 * distance_score
    }


def set_flights_scores(flights):
    for flight in flights:
        set_flight_scores(flight)

def set_hotels_scores(hotels):
    for hotel in hotels:
        set_hotel_scores(hotel)  

def get_best_flight(flights):
    flights = sorted(flights, key=lambda flight: flight["scores"]["preference_score"], reverse=True)

    return flights[0]


def get_best_hotel(hotels):
    hotels = sorted(hotels, key=lambda hotel: hotel["scores"]["preference_score"], reverse=True)

    return hotels[0]


def set_flight_scores(flight):
    """Compute flight scores based on outbound segment."""
    outbound = flight["outbound"]
    flight_time = get_flight_time(outbound)  # in minutes
    connections = outbound.get("stops", 0)
    price = get_flight_price_usd(flight)

    flight["scores"] = {
        "price_score": calc_flight_score(flight_time, connections, price, mode="budget"),
        "quality_score": 0,          # can be extended
        "convenience_score": 0,      # can be extended
        "preference_score": calc_flight_score(flight_time, connections, price, mode="normal")
    }


def set_hotel_scores(hotel):
    """Compute hotel scores based on rating, price, amenities."""
    rating = hotel.get("rating", 0)
    price_per_night = get_hotel_price_usd(hotel)
    amenities_count = min(len(hotel.get("amenities", [])), 10)

    hotel["scores"] = {
        "price_score": calc_hotel_score(rating, price_per_night, amenities_count, mode="budget"),
        "quality_score": 0,         # can be extended
        "convenience_score": 0,     # can be extended
        "preference_score": calc_hotel_score(rating, price_per_night, amenities_count, mode="normal")
    }


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


def get_flight_time(segment):
    """Returns flight duration in minutes from a FlightSegment."""
    fmt = "%Y-%m-%dT%H:%M:%S"
    dep = segment["departure_time"]
    arr = segment["arrival_time"]
    delta = datetime.strptime(arr, fmt) - datetime.strptime(dep, fmt)
    return delta.total_seconds() / 60


def get_flight_price_usd(flight):
    """Convert flight price_per_person to USD."""
    price = flight["price_per_person"]["amount"]
    currency = flight["price_per_person"]["currency"]
    return price * EXCHANGE_RATES_TO_USD.get(currency, 1.0)


def get_hotel_price_usd(hotel):
    """Convert hotel price_per_night to USD."""
    price = hotel["price_per_night"]["amount"]
    currency = hotel["price_per_night"]["currency"]
    return price * EXCHANGE_RATES_TO_USD.get(currency, 1.0)
