from __future__ import annotations

import os
import json
import re
from typing import Optional
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone 
from shared.data_types.models import *
from fastapi import FastAPI, HTTPException
from amadeus import Client, ResponseError


# ----------------------------
# Config
# ----------------------------

AMADEUS_CLIENT_ID = 'puGK9MPfzMCHoI9hpC2SoebnuDMKeWbA'
AMADEUS_CLIENT_SECRET = 'Tizmh2XUrjV6rRAb'

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


# ----------------------------
# Helpers
# ----------------------------

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


def _iso_to_dt(s: str) -> Optional[datetime]:
    """
    Amadeus returns ISO timestamps, usually with timezone offsets.
    Example: '2026-04-05T10:30:00' or '2026-04-05T10:30:00+02:00' or '...Z'
    """
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def _minutes_between(start_iso: str, end_iso: str) -> int:
    start = _iso_to_dt(start_iso)
    end = _iso_to_dt(end_iso)
    if not start or not end:
        return 0
    delta = end - start
    return max(0, int(delta.total_seconds() // 60))


def _get_location_meta(locations: Dict[str, Any], iata: str) -> Dict[str, Any]:
    """
    locations is expected to come from resp.result['dictionaries']['locations'].
    """
    if not locations or not iata:
        return {}
    return locations.get(iata, {}) or {}


def _is_overnight(start_iso: str, end_iso: str) -> bool:
    if not start_iso or not end_iso:
        return False
    try:
        start_dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
        return start_dt.date() != end_dt.date()
    except Exception:
        return False

def _offer_to_flight_option(
    offer: Dict[str, Any],
    passengers: int = 1,
    locations: Optional[Dict[str, Any]] = None,   # <--- NEW
) -> FlightOption:
    locations = locations or {}
    
    # --- Pricing ---
    price_info = offer.get("price", {}) or {}
    currency = price_info.get("currency") or "USD"
    total_amount = _safe_float(price_info.get("grandTotal") or price_info.get("total"))

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
    if segments:
        path = " -> ".join(
            (s.get("departure", {}).get("iataCode", "?") + "-" + s.get("arrival", {}).get("iataCode", "?"))
            for s in segments
        )
    # Defaults
    origin_loc = Location()
    dest_loc = Location()
    departure_time = ""
    arrival_time = ""
    airline = ""
    flight_number = ""
    aircraft = ""
    cabin_class = ""

    # First & last segment give route + times
    if segments:
        first_seg = segments[0]
        last_seg = segments[-1]

        dep = first_seg.get("departure", {}) or {}
        arr = last_seg.get("arrival", {}) or {}

        origin_code = dep.get("iataCode", "") or ""
        dest_code = arr.get("iataCode", "") or ""

        # OPTIONAL: enrich origin/destination with dictionaries if your Location model supports it
        origin_meta = _get_location_meta(locations, origin_code)
        dest_meta = _get_location_meta(locations, dest_code)

        origin_loc = _loc_from_iata(origin_code, locations)
        dest_loc = _loc_from_iata(dest_code, locations)


        
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
        seg_in = segments[i] or {}
        seg_out = segments[i + 1] or {}

        a = seg_in.get("arrival", {}) or {}
        b = seg_out.get("departure", {}) or {}

        layover_airport = a.get("iataCode", "") or ""
        layover_start = a.get("at", "") or ""
        layover_end = b.get("at", "") or ""

        layover_duration = _minutes_between(layover_start, layover_end)

        arrival_terminal = a.get("terminal")
        departure_terminal = b.get("terminal")

        layovers.append(
            Layover(
                airport=_loc_from_iata(layover_airport, locations),


                start_time=layover_start,
                end_time=layover_end,
                duration_minutes=layover_duration,

                arrival_terminal=arrival_terminal,
                departure_terminal=departure_terminal,

                airline_before=seg_in.get("carrierCode", "") or "",
                airline_after=seg_out.get("carrierCode", "") or "",

                is_airline_change=(seg_in.get("carrierCode", "") != seg_out.get("carrierCode", "")),
                is_terminal_change=(arrival_terminal is not None and departure_terminal is not None and arrival_terminal != departure_terminal),
                overnight=_is_overnight(layover_start, layover_end),
            )
        )



    # Cabin class (best source is fareDetailsBySegment)
    if traveler_pricings:
        fds = traveler_pricings[0].get("fareDetailsBySegment", []) or []
        if fds:
            cabin_class = (fds[0].get("cabin") or "").lower()

    amenities = AmenityInfo()
    luggage = LuggageInfo()

    if traveler_pricings:
        fds_list = traveler_pricings[0].get("fareDetailsBySegment", []) or []
        if fds_list:
            fds0 = fds_list[0]

            amenities = _parse_amenities_from_fds(fds0)
            luggage = _parse_luggage_from_fds(fds0)


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
        luggage=luggage,
    )

    provider = ""
    vac = offer.get("validatingAirlineCodes", []) or []
    provider = vac[0] if vac else airline

    return FlightOption(
        id=str(offer.get("id", "")),
        outbound=outbound_seg,
        total_price=total_price,
        price_per_person=price_per_person,
        scores=ComponentScores(),
        booking_url="",
        provider=provider,
        available=True,
    )

def explore(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{prefix}{k}: {type(v).__name__}")
            explore(v, prefix + "  ")
    elif isinstance(obj, list) and obj:
        print(f"{prefix}[list of {type(obj[0]).__name__}]")
        explore(obj[0], prefix + "  ")


@app.post("/api/flight_retriever/search", response_model=FlightSearchResponse)
def flight_search(request: FlightSearchRequest):

    if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Missing AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET env vars")

    if not request.origin.airport_code or not request.destination.airport_code or not request.departure_date:
        raise HTTPException(
            status_code=400,
            detail="origin.airport_code, destination.airport_code, and departure_date are required",
        )

    origin_code = request.origin.airport_code.strip().upper()
    dest_code = request.destination.airport_code.strip().upper()
    departure_date = request.departure_date.strip()
    adults = max(1, int(request.passengers or 1))

    max_results = 250  # your decision

    try:
        resp = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=dest_code,
            departureDate=departure_date,
            adults=adults,
            max=max_results,
        )

        result = getattr(resp, "result", None) or {}
        dictionaries = result.get("dictionaries", {}) or {}
        locations = dictionaries.get("locations", {}) or {}
        

        offers = resp.data or []

        flight_options: list[FlightOption] = [
            _offer_to_flight_option(
                o,
                passengers=adults,
                locations=locations,
            )
            for o in offers
        ]

        # ---- build metadata (fill what you have in your SearchMetadata model) ----
        metadata = SearchMetadata(
            origin=origin_code,
            destination=dest_code,
            departure_date=departure_date,
            passengers=adults,
            returned_count=len(flight_options),
            requested_max=max_results,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
        )

        return FlightSearchResponse(options=flight_options, metadata=metadata)

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Amadeus error: {e}")

# ----------------------------
# Local run helper (optional)
# ----------------------------

def pretty_print_flights_response(resp: "FlightSearchResponse") -> None:
    flights = resp.options or []

    print("\n" + "=" * 90)
    print(f"✈️  FOUND {len(flights)} FLIGHT OPTIONS")
    print("=" * 90)

    for i, fo in enumerate(flights, start=1):
        outbound = fo.outbound

        origin = (outbound.origin.airport_code or "") if outbound.origin else ""
        destination = (outbound.destination.airport_code or "") if outbound.destination else ""

        total_price = fo.total_price
        per_person = fo.price_per_person

        print(f"\n🧳 FLIGHT #{i}")
        print("-" * 90)

        print(f"ID        : {fo.id or ''}")
        print(f"Provider  : {fo.provider or ''}")
        print(f"Available : {bool(fo.available)}")

        print("\nROUTE")
        print(f"  {origin} ➜ {destination}")

        print("\nTIMES")
        print(f"  Departure : {outbound.departure_time or ''}")
        print(f"  Arrival   : {outbound.arrival_time or ''}")
        h, m = divmod(outbound.duration_minutes, 60)
        print(f"  Duration  : {int(h)}h {int(m)}m")

        print("\nFLIGHT INFO")
        print(f"  Airline   : {outbound.airline or ''}")
        print(f"  Flight No : {outbound.flight_number or ''}")
        print(f"  Aircraft  : {outbound.aircraft or ''}")
        print(f"  Cabin     : {outbound.cabin_class or ''}")
        print(f"  Stops     : {int(outbound.stops or 0)}")

        layovers = outbound.layovers or []
        print("\nLAYOVERS")
        if not layovers:
            print("  Direct flight")
        else:
            for idx, l in enumerate(layovers, start=1):
                airport_code = l.airport.airport_code or "(unknown airport)"

                start = l.start_time or ""
                end = l.end_time or ""
                duration = int(l.duration_minutes or 0)

                arrival_terminal: Optional[str] = l.arrival_terminal
                departure_terminal: Optional[str] = l.departure_terminal

                airline_before = l.airline_before or ""
                airline_after = l.airline_after or ""

                is_airline_change = bool(l.is_airline_change)
                is_terminal_change = bool(l.is_terminal_change)
                overnight = bool(l.overnight)

                print(f"  ✈ Stop #{idx} at {airport_code}")
                print(f"     Time     : {start} → {end}")

                # Terminals (optional)
                term_bits = []
                if arrival_terminal:
                    term_bits.append(f"Arr T{arrival_terminal}")
                if departure_terminal:
                    term_bits.append(f"Dep T{departure_terminal}")
                if term_bits:
                    print(
                        f"     Terminal : " + " → ".join(term_bits)
                        if len(term_bits) == 2
                        else f"     Terminal : {term_bits[0]}"
                    )

                # Layover duration
                if duration:
                    h, m = divmod(duration, 60)
                    print(f"     Layover  : {h}h {m}m" if h else f"     Layover  : {m}m")

                # Change flags (optional but useful)
                flags = []
                if is_airline_change:
                    flags.append(f"Airline change ({airline_before} → {airline_after})")
                if is_terminal_change:
                    flags.append("Terminal change")
                if overnight:
                    flags.append("Overnight")
                if flags:
                    print(f"     Notes    : " + " | ".join(flags))

        print("\nPRICE")
        print(f"  Total     : {total_price.amount or 0} {total_price.currency or ''}")
        print(f"  Per person: {per_person.amount or 0} {per_person.currency or ''}")

        print("\n" + "-" * 90)

    print("\n" + "=" * 90 + "\n")
    print(f"✈️  FOUND {len(flights)} FLIGHT OPTIONS")


def _loc_from_iata(iata: str, locations: Dict[str, Any]) -> Location:
    """
    Build a Location with city/country/lat/lon using Amadeus dictionaries.locations.
    Falls back safely if fields are missing.
    """
    meta = _get_location_meta(locations, iata) or {}
    geo = meta.get("geoCode", {}) or {}

    return Location(
        airport_code=iata or "",
        city=meta.get("cityName", "") or "",
        country=meta.get("countryCode", "") or "",
        latitude=float(geo.get("latitude") or 0.0),
        longitude=float(geo.get("longitude") or 0.0),
    )


def _parse_amenities_from_fds(fds: Dict[str, Any]) -> AmenityInfo:
    """
    Amadeus amenities are usually a list with descriptions, not booleans.
    We'll infer booleans by keyword matching.
    """
    info = AmenityInfo()

    ams = fds.get("amenities", []) or []
    for a in ams:
        desc = (a.get("description") or "").lower()

        if "wi-fi" in desc or "wifi" in desc:
            info.wifi = True
        if "meal" in desc or "food" in desc:
            info.meal = True
        if "entertainment" in desc:
            info.entertainment = True
        if "power" in desc or "usb" in desc or "outlet" in desc:
            info.power_outlet = True

    # legroom_inches is not provided by Flight Offers Search -> keep default 0
    return info


def _parse_luggage_from_fds(fds: Dict[str, Any]) -> LuggageInfo:
    """
    Correctly map Amadeus includedCheckedBags / includedCabinBags.
    """
    luggage = LuggageInfo()

    checked = fds.get("includedCheckedBags") or {}
    if checked:
        luggage.checked_bags = int(checked.get("quantity") or 0)

        weight = checked.get("weight")
        unit = (checked.get("weightUnit") or "").upper()
        if weight is not None and unit == "KG":
            luggage.checked_bag_weight_kg = float(weight)

    cabin = fds.get("includedCabinBags") or {}
    if cabin:
        luggage.carry_on_bags = int(cabin.get("quantity") or 0)

        # Usually no weight/dimensions in this endpoint
        # luggage.carry_on_weight_kg = ...
        # luggage.carry_on_dimensions_cm = ...

    return luggage

if __name__ == "__main__":
    try:
        FlightReq = FlightSearchRequest(
            origin=Location(airport_code="LHR"),
            destination=Location(airport_code="JFK"),
            departure_date="2026-04-05",
            passengers=2,
        )
        
        flight_response = flight_search(FlightReq)
        print(json.dumps(flight_response.dict(), indent=2))
    except ResponseError as error:
        print(error)
