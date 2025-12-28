from datetime import datetime

EXCHANGE_RATES_TO_USD = {
    "USD": 1.0,
    "EUR": 1.084,
    "GBP": 1.27,
    "ILS": 0.27
}


def give_packages_scores(pairs):
    for pair in pairs:
        set_package_score(pair)    

def set_package_score(pair):
    set_hotel_scores(pair["hotel"])
    hotel_scores = pair["hotel"]["scores"]

    flight = pair["cheapest_flight"]
    set_flight_scores(flight)
    flight_scores = flight["scores"]

    distance = pair["distance_km"] # Between airport and hotel
    ref_distance = 50
    distance_score = 1 - min(distance / ref_distance, 1)

    pair["scores"]["normal"] = 0.4 * flight_scores["normal"] + 0.4 * hotel_scores["normal"] + 0.2 * distance_score
    pair["scores"]["budget"] = 0.4 * flight_scores["budget"] + 0.4 * hotel_scores["budget"] + 0.2 * distance_score


def set_flight_scores(flight):
    flight_time = get_flight_time(flight) / 60
    connections = flight["connections"]
    price = get_flight_price_usd(flight)

    flight["scores"]["normal"] = calc_flight_score(flight_time, connections, price, "normal")
    flight["scores"]["budget"] = calc_flight_score(flight_time, connections, price, "budget")
    flight["scores"]["duration"] = calc_flight_score(flight_time, connections, price, "duration")

    
def set_hotel_scores(hotel):
    rating = hotel["rating"]
    price_per_night = get_hotel_price_usd(hotel)
    amenities = min(len(hotel["amenities"]), 10)

    hotel["scores"]["normal"] = calc_hotel_score(rating, price_per_night, amenities, "normal")
    hotel["scores"]["budget"] = calc_hotel_score(rating, price_per_night, amenities, "budget")

def calc_hotel_score(rating, price_per_night, amenities, mode="normal"):
    ref_price = 1500       #  max expected price in USD
    ref_rating = 5
    ref_amenities = 10
    if mode == "normal":
        score = 0.5 * (rating/ref_rating) + 0.3 * (price_per_night/ref_price) + 0.2 * (amenities / ref_amenities)
    elif mode == "budget":
        score = 0.3 * (rating/ref_rating) + 0.6 * (price_per_night/ref_price) + 0.1 * (amenities / ref_amenities)


    return score



def calc_flight_score(flight_time, connections, price, mode="normal"):
    ref_price = 1000       #  max expected price in USD
    ref_duration = 720     #  max flight duration in minutes (12h)
    ref_connections = 2    #  maximum considered connections
    if mode == "normal":
        score = 0.5 * (price/ref_price) + 0.35 * (flight_time / ref_duration) + 0.15 * (connections/ref_connections)
    elif mode == "budget":
        score = 0.7 * (price/ref_price) + 0.25 * (flight_time / ref_duration) + 0.05 * (connections/ref_connections)
    else: # mode == duration   MAYBE in the future
        score = 0.3 * (price/ref_price) + 0.65 * (flight_time / ref_duration) + 0.05 * (connections/ref_connections)

    return 1 - min(score, 1) # Higher better



def get_flight_time(flight):
    format = "%Y-%m-%dT%H:%M:%S"

    delta = datetime.strptime(flight["arrival_time"], format) - datetime.strptime(flight["depart_time"], format)

    print(delta)
    print(delta.total_seconds)
    flight["flight_time"] = delta.total_seconds
    return delta.total_seconds

def get_flight_price_usd(flight):
    flight["in_USD"] = flight["price"] * EXCHANGE_RATES_TO_USD[flight["currency"]]
    return flight["in_USD"]

def get_hotel_price_usd(hotel):
   return hotel["price_per_night"] * EXCHANGE_RATES_TO_USD[hotel["currency"]]
