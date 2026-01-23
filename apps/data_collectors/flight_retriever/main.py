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
from dotenv import load_dotenv
<<<<<<< Updated upstream
import os
=======

from .data_processor import transform_flight_data, generate_unique_flight_id
from .default_flights import get_default_flights_by_route, get_default_flight_by_id
>>>>>>> Stashed changes
# ----------------------------
# Config
# ----------------------------

load_dotenv()

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
    raise RuntimeError("Missing Amadeus credentials – check .env")

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
async def flight_search(request: FlightSearchRequest):

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
<<<<<<< Updated upstream
=======
        if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
            raise RuntimeError("Missing AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET env vars")
        # Check if entire search is cached (Optional, but good for performance)
        search_cache_key = f"flight_search:{origin_code}:{dest_code}:{departure_date}:{adults}"
        cached_response = await cache_get(search_cache_key)
        if cached_response:
            print(f"Cache hit for search {search_cache_key}")
            return FlightSearchResponse.model_validate(cached_response)

        print(f"Cache miss for search {search_cache_key}, calling Amadeus...")
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Amadeus error: {e}")


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
=======
        return response

    except (ResponseError, Exception) as e:
        # Fallback to default flights
        print(f"Amadeus API failed or error occurred: {e}. Falling back to default flights...")
        
        default_flights_data = get_default_flights_by_route(request.origin.city, request.destination.city)
        
        if not default_flights_data:
            # Try by airport codes if city names didn't match
            default_flights_data = get_default_flights_by_route(origin_code, dest_code)

        if default_flights_data:
            flight_options = [FlightOption.model_validate(f) for f in default_flights_data]
            
            metadata = SearchMetadata(
                total_results=len(flight_options),
                search_id=f"default_flight_search_{datetime.now(timezone.utc).timestamp()}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                data_source="Default Fallback Data",
            )
            
            return FlightSearchResponse(options=flight_options, metadata=metadata)

        # If no default flights either, then raise the original error
        if isinstance(e, ResponseError):
            status_code = getattr(e.response, "status_code", 502)
            error_body = getattr(e.response, "body", None) or {}
            errors = error_body.get("errors", []) if isinstance(error_body, dict) else []
            detail_msg = errors[0].get("detail", str(e)) if errors else str(e)
            raise HTTPException(status_code=status_code, detail=f"Amadeus error (and no fallback available): {detail_msg}")
        
        raise HTTPException(status_code=502, detail=f"Amadeus error (and no fallback available): {e}")


@app.get("/api/flight_retriever/flights/{flight_id}")
async def get_flight_details(flight_id: str):
    """Get raw offer details from provider using unique mapping or default data"""
    # Check if it's a default flight
    if flight_id.startswith("default_f_"):
        default_flight = get_default_flight_by_id(flight_id)
        if default_flight:
            return default_flight
            
    offer = await get_provider_offer(flight_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Flight offer not found in cache or expired")
    return offer


@app.post("/api/flight_retriever/flights/{flight_id}/price")
async def verify_price(flight_id: str):
    """Verify current price and availability for a flight offer or default data"""
    # Check if it's a default flight
    if flight_id.startswith("default_f_"):
        default_flight = get_default_flight_by_id(flight_id)
        if default_flight:
            # For default flights, we just return the flight itself as "verified"
            return {"data": default_flight, "status": "verified", "source": "default_data"}

    offer = await get_provider_offer(flight_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Flight offer not found in cache or expired")
    
    try:
        # Call Amadeus Pricing API to verify
        # Note: This requires the full raw offer object
        price_resp = amadeus.shopping.flight_offers.pricing.post(offer)
        return price_resp.result
    except ResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
>>>>>>> Stashed changes


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

