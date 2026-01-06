from __future__ import annotations
import json

from fastapi import FastAPI



from typing import Any, Dict, List, Optional


def title_case(s: Optional[str]) -> Optional[str]:
    if not s:
        return s
    # Your data is mostly uppercase; this makes it nicer for UI.
    return s.strip().title()


def parse_amadeus_locations(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse the Amadeus locations response (list of dicts) into a clean list like:

    {
      "name": "...",
      "iata": "...",
      "city": "...",
      "country": "...",
      "countryCode": "...",
      "timezone": "...",
      "location": {"lat": ..., "lng": ...},
      "popularityScore": ...
    }

    - Keeps only AIRPORT items that have iataCode + geoCode.
    - Sorts by popularityScore desc, then by name.
    """
    cleaned: List[Dict[str, Any]] = []

    for item in raw:
        if item.get("subType") != "AIRPORT":
            continue

        iata = item.get("iataCode")
        geo = item.get("geoCode") or {}
        lat = geo.get("latitude")
        lng = geo.get("longitude")

        # Must-have fields for your UI/use-case
        if not iata or lat is None or lng is None:
            continue

        address = item.get("address") or {}
        travelers = ((item.get("analytics") or {}).get("travelers") or {})
        score = travelers.get("score")

        name_raw = item.get("name")
        # Prefer detailedName if you want more specificity; here we keep a nicer name.
        display_name = title_case(name_raw) or iata

        country = title_case(address.get("countryName"))
        city = title_case(address.get("cityName"))

        cleaned.append(
            {
                "name": display_name,
                "iata": iata,
                "city": city,
                "country": country,
                "countryCode": address.get("countryCode"),
                "timezone": item.get("timeZoneOffset"),
                "location": {"lat": float(lat), "lng": float(lng)},
                "popularityScore": int(score) if isinstance(score, (int, float)) else None,
            }
        )

    # Sort: higher popularity first; missing scores go to the bottom
    def sort_key(x: Dict[str, Any]):
        score = x.get("popularityScore")
        score_key = score if isinstance(score, int) else -1
        return (-score_key, x.get("name") or "")

    cleaned.sort(key=sort_key)
    return cleaned


def group_by_city(airports: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group parsed airports by city:
    {
      "London": [ ... ],
      "Guiyang": [ ... ]
    }
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for a in airports:
        city = a.get("city") or "Unknown"
        grouped.setdefault(city, []).append(a)

    # Optional: sort each city group by popularity desc
    for city, items in grouped.items():
        items.sort(key=lambda x: -(x.get("popularityScore") or -1))
    return grouped


def top_n(airports: List[Dict[str, Any]], n: int = 5) -> List[Dict[str, Any]]:
    """Return top N by popularityScore (assumes parse_amadeus_locations already sorted)."""
    return airports[: max(0, int(n))]



app = FastAPI(title="Flight Retriever Service")

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

from amadeus import Client, Location, ResponseError

amadeus = Client(
    client_id='puGK9MPfzMCHoI9hpC2SoebnuDMKeWbA',
    client_secret='Tizmh2XUrjV6rRAb'
)

def pretty_print(data, max_items: int = 10, separator: str = "----------------------------------------------------"):
    """
    Pretty-print the response. If `data` is a list, print up to `max_items` entries,
    printing each item separately and inserting `separator` between entries. A small
    summary with the total count is printed first.
    """
    if isinstance(data, list):
        total = len(data)
        shown = data[:max_items]

        # Summary header
        print(json.dumps({"total": total, "shown": len(shown)}, indent=2, ensure_ascii=False))

        # Print each item and insert a separator between items
        for i, item in enumerate(shown):
            print(json.dumps(item, indent=2, ensure_ascii=False))
            if i != len(shown) - 1:
                print(separator)

        # If there are more items, show a final note
        if total > len(shown):
            print(separator)
            print(f"...and {total - len(shown)} more items")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    try:
        response = amadeus.shopping.flight_offers_search.get(
        originLocationCode="TLV",
        destinationLocationCode="LON",
        departureDate="2026-03-10",
        adults=1,
        max=250   # maximum allowed per page
    )
        pretty_print(response.data)


    except ResponseError as error:
        print(error)
