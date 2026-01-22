import uuid
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from shared.data_types.models import (
    FlightOption, FlightSegment, Location, Money, 
    Layover, AmenityInfo, LuggageInfo, ComponentScores
)

def _parse_iso_duration_to_minutes(d: str) -> int:
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

def _is_overnight(start_iso: str, end_iso: str) -> bool:
    if not start_iso or not end_iso:
        return False
    try:
        start_dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
        return start_dt.date() != end_dt.date()
    except Exception:
        return False

def _loc_from_iata(iata: str, locations: Dict[str, Any]) -> Location:
    meta = locations.get(iata, {}) or {}
    geo = meta.get("geoCode", {}) or {}

    return Location(
        airport_code=iata or "",
        city=meta.get("cityName", "") or "",
        country=meta.get("countryCode", "") or "",
        latitude=float(geo.get("latitude") or 0.0),
        longitude=float(geo.get("longitude") or 0.0),
    )

def _parse_amenities_from_fds(fds: Dict[str, Any]) -> AmenityInfo:
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
    return info

def _parse_luggage_from_fds(fds: Dict[str, Any]) -> LuggageInfo:
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
    return luggage

def generate_unique_flight_id(segments: List[Dict[str, Any]]) -> str:
    """Generate a deterministic unique ID based on flight segments"""
    sig_parts = []
    for seg in segments:
        # Carrier + FlightNo + Origin + Destination + DepartureTime
        part = f"{seg.get('carrierCode','')}{seg.get('number','')}_{seg.get('departure',{}).get('iataCode','')}-{seg.get('arrival',{}).get('iataCode','')}_{seg.get('departure',{}).get('at','')}"
        sig_parts.append(part)
    
    unique_string = "|".join(sig_parts)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

def transform_flight_data(
    offer: Dict[str, Any],
    passengers: int = 1,
    locations: Optional[Dict[str, Any]] = None,
) -> FlightOption:
    """Transform Amadeus flight offer to FlightOption Pydantic model"""
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

    origin_loc = Location()
    dest_loc = Location()
    departure_time = ""
    arrival_time = ""
    airline = ""
    flight_number = ""
    aircraft = ""
    cabin_class = ""

    if segments:
        first_seg = segments[0]
        last_seg = segments[-1]

        dep = first_seg.get("departure", {}) or {}
        arr = last_seg.get("arrival", {}) or {}

        origin_code = dep.get("iataCode", "") or ""
        dest_code = arr.get("iataCode", "") or ""

        origin_loc = _loc_from_iata(origin_code, locations)
        dest_loc = _loc_from_iata(dest_code, locations)
        
        departure_time = dep.get("at", "") or ""
        arrival_time = arr.get("at", "") or ""

        airline = first_seg.get("carrierCode", "") or ""
        flight_number = f"{airline}{first_seg.get('number', '')}"
        aircraft = (first_seg.get("aircraft", {}) or {}).get("code", "") or ""

    # Duration & stops
    duration_minutes = _parse_iso_duration_to_minutes(outbound_it.get("duration", ""))
    stops = max(0, len(segments) - 1)

    # Layovers
    layovers: List[Layover] = []
    for i in range(len(segments) - 1):
        seg_in = segments[i] or {}
        seg_out = segments[i + 1] or {}

        a = seg_in.get("arrival", {}) or {}
        b = seg_out.get("departure", {}) or {}

        layover_airport = a.get("iataCode", "") or ""
        layover_start = a.get("at", "") or ""
        layover_end = b.get("at", "") or ""

        layovers.append(
            Layover(
                airport=_loc_from_iata(layover_airport, locations),
                start_time=layover_start,
                end_time=layover_end,
                duration_minutes=_minutes_between(layover_start, layover_end),
                arrival_terminal=a.get("terminal"),
                departure_terminal=b.get("terminal"),
                airline_before=seg_in.get("carrierCode", "") or "",
                airline_after=seg_out.get("carrierCode", "") or "",
                is_airline_change=(seg_in.get("carrierCode", "") != seg_out.get("carrierCode", "")),
                is_terminal_change=(a.get("terminal") != b.get("terminal") if a.get("terminal") and b.get("terminal") else False),
                overnight=_is_overnight(layover_start, layover_end),
            )
        )

    if traveler_pricings:
        fds_list = traveler_pricings[0].get("fareDetailsBySegment", []) or []
        if fds_list:
            cabin_class = (fds_list[0].get("cabin") or "").lower()
            amenities = _parse_amenities_from_fds(fds_list[0])
            luggage = _parse_luggage_from_fds(fds_list[0])
        else:
            amenities = AmenityInfo()
            luggage = LuggageInfo()
    else:
        amenities = AmenityInfo()
        luggage = LuggageInfo()

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

    vac = offer.get("validatingAirlineCodes", []) or []
    provider = vac[0] if vac else airline

    # Generate Unique ID
    unique_id = generate_unique_flight_id(segments)

    return FlightOption(
        id=unique_id,
        outbound=outbound_seg,
        total_price=total_price,
        price_per_person=price_per_person,
        scores=ComponentScores(),
        booking_url="",
        provider=provider,
        available=True,
    )
