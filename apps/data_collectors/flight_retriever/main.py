

from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Optional, Tuple
from shared.data_types.models import *
from fastapi import FastAPI, HTTPException
from amadeus import Client, ResponseError


# ----------------------------
# Config
# ----------------------------

AMADEUS_CLIENT_ID = 'puGK9MPfzMCHoI9hpC2SoebnuDMKeWbA'
AMADEUS_CLIENT_SECRET = 'Tizmh2XUrjV6rRAb'

if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
    # You can still run locally if you want by exporting env vars.
    # On Linux/Mac:
    #   export AMADEUS_CLIENT_ID="..."
    #   export AMADEUS_CLIENT_SECRET="..."
    # On Windows (PowerShell):
    #   setx AMADEUS_CLIENT_ID "..."
    #   setx AMADEUS_CLIENT_SECRET "..."
    pass

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET,
)

app = FastAPI(title="Flight Retriever Service")

# ----------------------------
# FastAPI endpoints
# ----------------------------

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}


@app.get("/health")
async def health():
    return {"status": "ok"}

import re
from typing import Any, Dict, List, Optional

def _parse_iso_duration_to_minutes(d: str) -> int:
    """
    Amadeus uses ISO 8601 durations like 'PT6H17M' or 'PT50M'.
    """
    if not d:
        return 0
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", d)
    if not m:
        return 0
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    return hours * 60 + minutes


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _offer_to_flight_option(offer: Dict[str, Any], passengers: int = 1) -> FlightOption:
    # --- Pricing ---
    price_info = offer.get("price", {}) or {}
    currency = price_info.get("currency") or "USD"
    total_amount = _safe_float(price_info.get("grandTotal") or price_info.get("total"))

    # Prefer travelerPricings[0] if present (per person)
    traveler_pricings = offer.get("travelerPricings", []) or []
    if traveler_pricings:
        per_person_amount = _safe_float(traveler_pricings[0].get("price", {}).get("total"))
    else:
        per_person_amount = total_amount / max(1, passengers)

    total_price = Money(currency=currency, amount=total_amount)
    price_per_person = Money(currency=currency, amount=per_person_amount)

    # --- Outbound itinerary & segments ---
    itineraries = offer.get("itineraries", []) or []
    outbound_it = itineraries[0] if itineraries else {}
    segments = outbound_it.get("segments", []) or []

    # Defaults
    origin_loc = Location()
    dest_loc = Location()
    departure_time = ""
    arrival_time = ""
    airline = ""
    flight_number = ""
    aircraft = ""
    cabin_class = ""  # comes from fareDetailsBySegment, not always in segment

    # First & last segment give route + times
    if segments:
        first_seg = segments[0]
        last_seg = segments[-1]

        dep = first_seg.get("departure", {}) or {}
        arr = last_seg.get("arrival", {}) or {}

        origin_loc = Location(airport_code=dep.get("iataCode", ""))
        dest_loc = Location(airport_code=arr.get("iataCode", ""))

        departure_time = dep.get("at", "") or ""
        arrival_time = arr.get("at", "") or ""

        airline = first_seg.get("carrierCode", "") or ""
        flight_number = (first_seg.get("carrierCode", "") or "") + (first_seg.get("number", "") or "")
        aircraft = (first_seg.get("aircraft", {}) or {}).get("code", "") or ""

    # Duration & stops
    duration_minutes = _parse_iso_duration_to_minutes(outbound_it.get("duration", ""))
    stops = max(0, len(segments) - 1)

    # Layovers: between seg i and seg i+1
    layovers: List[Layover] = []
    for i in range(len(segments) - 1):
        a = segments[i].get("arrival", {}) or {}
        b = segments[i + 1].get("departure", {}) or {}

        layover_airport = a.get("iataCode", "")
        layover_start = a.get("at", "")
        layover_end = b.get("at", "")

        layovers.append(
            Layover(
                airport_code=layover_airport,
                start_time=layover_start,
                end_time=layover_end,
                duration_minutes=0,  # optional: compute from timestamps if you want
            )
        )

    # Cabin class (best source is fareDetailsBySegment)
    if traveler_pricings:
        fds = traveler_pricings[0].get("fareDetailsBySegment", []) or []
        if fds:
            cabin_class = (fds[0].get("cabin") or "").lower()  # "ECONOMY" -> "economy"

    # Amenities (optional): extract a small summary from fareDetailsBySegment
    amenities = AmenityInfo()
    if traveler_pricings:
        fds = traveler_pricings[0].get("fareDetailsBySegment", []) or []
        if fds:
            ams = fds[0].get("amenities", []) or []
            # Example: store a few strings; depends on your AmenityInfo schema
            # If AmenityInfo has "items: List[str]" for example:
            try:
                amenities.items = [a.get("description", "") for a in ams if a.get("description")]
            except Exception:
                pass

    outbound_seg = FlightSegment(
        origin=origin_loc,
        destination=dest_loc,
        departure_time=departure_time,
        arrival_time=arrival_time,
        duration_minutes=duration_minutes,
        stops=stops,
        layovers=layovers,
        airline=airline,
        flight_number=flight_number,
        aircraft=aircraft,
        cabin_class=cabin_class,
        amenities=amenities,
    )

    # Provider: use validating airline if present, else segment carrier
    provider = ""
    vac = offer.get("validatingAirlineCodes", []) or []
    if vac:
        provider = vac[0]
    else:
        provider = airline

    return FlightOption(
        id=str(offer.get("id", "")),
        outbound=outbound_seg,
        total_price=total_price,
        price_per_person=price_per_person,
        scores=ComponentScores(),   # you can fill later
        booking_url="",             # Amadeus search doesn’t give booking URL
        provider=provider,
        available=True,
    )

@app.post("/api/flight_retriever/search")
def flight_search(request: FlightSearchRequest):
    

    if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Missing AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET env vars")

    # Basic validation
    if not request.origin.airport_code or not request.destination.airport_code or not request.departure_date:
        raise HTTPException(
            status_code=400,
            detail="origin.airport_code, destination.airport_code, and departure_date are required",
        )

    # Normalize & safe defaults
    origin_code = request.origin.airport_code.strip().upper()
    dest_code = request.destination.airport_code.strip().upper()
    departure_date = request.departure_date.strip()
    adults = max(1, int(request.passengers or 1))

    max_results = request.max_results if request.max_results and request.max_results > 0 else 20
    max_results = max(1, min(250, int(max_results)))  

    try:
        resp = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=dest_code,
            departureDate=departure_date, 
            adults=adults, 
            max=max_results
        )
        offers = resp.data or []
        flight_options = [
            _offer_to_flight_option(o, passengers=adults)  # adults == number of travelers
            for o in offers
        ]
        return [fo.model_dump() for fo in flight_options]

    
    except ResponseError as e:
        # expose Amadeus' real error payload when possible
        detail = str(e)
        try:
            detail = e.response.result
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=detail)
# ----------------------------
# Local run helper (optional)
# ----------------------------
def pretty_print_flights_dump(flights: list[dict]) -> None:
    print("\n" + "=" * 90)
    print(f"✈️  FOUND {len(flights)} FLIGHT OPTIONS")
    print("=" * 90)

    for i, fo in enumerate(flights, start=1):
        outbound = fo.get("outbound", {}) or {}
        origin = (outbound.get("origin", {}) or {}).get("airport_code", "")
        destination = (outbound.get("destination", {}) or {}).get("airport_code", "")

        total_price = fo.get("total_price", {}) or {}
        per_person = fo.get("price_per_person", {}) or {}

        print(f"\n🧳 FLIGHT #{i}")
        print("-" * 90)

        print(f"ID        : {fo.get('id', '')}")
        print(f"Provider  : {fo.get('provider', '')}")
        print(f"Available : {fo.get('available', False)}")

        print("\nROUTE")
        print(f"  {origin} ➜ {destination}")

        print("\nTIMES")
        print(f"  Departure : {outbound.get('departure_time', '')}")
        print(f"  Arrival   : {outbound.get('arrival_time', '')}")
        print(f"  Duration  : {outbound.get('duration_minutes', 0)} minutes")

        print("\nFLIGHT INFO")
        print(f"  Airline   : {outbound.get('airline', '')}")
        print(f"  Flight No : {outbound.get('flight_number', '')}")
        print(f"  Aircraft  : {outbound.get('aircraft', '')}")
        print(f"  Cabin     : {outbound.get('cabin_class', '')}")
        print(f"  Stops     : {outbound.get('stops', 0)}")

        layovers = outbound.get("layovers", []) or []
        print("\nLAYOVERS")
        if not layovers:
            print("  Direct flight")
        else:
            for l in layovers:
                print(
                    f"  - {l.get('airport_code','')} "
                    f"({l.get('start_time','')} → {l.get('end_time','')})"
                )

        print("\nPRICE")
        print(f"  Total     : {total_price.get('amount', 0)} {total_price.get('currency', '')}")
        print(f"  Per person: {per_person.get('amount', 0)} {per_person.get('currency', '')}")

        print("\n" + "-" * 90)

    print("\n" + "=" * 90 + "\n")

if __name__ == "__main__":
    # Quick local test without running the server:
    try:
        FlightReq = FlightSearchRequest(
            origin=Location(airport_code="JFK"),
            destination=Location(airport_code="LAX"),
            departure_date="2026-04-05",
            passengers=2
        )
        pretty_print_flights_dump(flight_search(FlightReq))
    except ResponseError as error:
        print(error)
