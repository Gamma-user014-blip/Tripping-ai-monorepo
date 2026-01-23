# Default Flights Data

This file contains default/fallback flight data to use when the flights API is unavailable.

## Overview

The `default_flights.py` file provides realistic sample flight data for common routes around the world. This ensures your application can continue functioning even when the external flights API is down.

## Available Routes

The following routes have default flight data:

1. **New York (JFK) → London (LHR)**
   - Direct flights: British Airways, Virgin Atlantic
   - Budget option: Aer Lingus (via Dublin)

2. **London (LHR) → New York (JFK)**
   - Direct flight: British Airways

3. **Los Angeles (LAX) → Tokyo (NRT)**
   - Direct flight: Japan Airlines

4. **Paris (CDG) → Barcelona (BCN)**
   - Direct flight: Air France

5. **Dubai (DXB) → Singapore (SIN)**
   - Direct flight: Emirates

6. **Sydney (SYD) → Melbourne (MEL)**
   - Direct flight: Qantas (domestic)

## Usage

### Import the module

```python
from shared.data_types.default_flights import (
    get_default_flights_by_route,
    get_all_default_flights,
    get_default_flight_by_id,
    get_available_routes
)
```

### Get flights for a specific route

```python
# Get all flights from New York to London
flights = get_default_flights_by_route("New York", "London")

# Returns a list of flight dictionaries matching the FlightOption model
for flight in flights:
    print(f"{flight['airline']} - ${flight['price_per_person']['amount']}")
```

### Get all available default flights

```python
# Get all default flights across all routes
all_flights = get_all_default_flights()
print(f"Total default flights available: {len(all_flights)}")
```

### Get a specific flight by ID

```python
# Get a specific flight
flight = get_default_flight_by_id("default_f_ny_ldn_1")
if flight:
    print(f"Found: {flight['airline']} {flight['outbound']['flight_number']}")
```

### Get list of available routes

```python
# See what routes have default data
routes = get_available_routes()
for origin, destination in routes:
    print(f"{origin} → {destination}")
```

## Integration Example

Here's how to integrate this into your flight retrieval service:

```python
from shared.data_types.default_flights import get_default_flights_by_route
import logging

def get_flights(origin: str, destination: str):
    try:
        # Try to get flights from the API
        response = flight_api.search(origin, destination)
        return response.options
    except Exception as e:
        logging.warning(f"Flight API unavailable: {e}. Using default flights.")
        # Fallback to default flights
        default_flights = get_default_flights_by_route(origin, destination)
        if default_flights:
            logging.info(f"Using {len(default_flights)} default flights for {origin} → {destination}")
            return default_flights
        else:
            logging.error(f"No default flights available for {origin} → {destination}")
            return []
```

## Data Format

All flight data follows the `FlightOption` model from `shared/data_types/models.py`:

```python
{
    "id": str,                    # Unique identifier
    "outbound": {                 # FlightSegment
        "origin": Location,
        "destination": Location,
        "departure_time": str,    # ISO 8601 format
        "arrival_time": str,
        "duration_minutes": int,
        "stops": int,
        "layovers": List[Layover],
        "airline": str,
        "flight_number": str,
        "aircraft": str,
        "cabin_class": str,
        "amenities": AmenityInfo,
        "luggage": LuggageInfo,
    },
    "total_price": Money,
    "price_per_person": Money,
    "scores": ComponentScores,
    "booking_url": str,
    "provider": str,
    "available": bool,
}
```

## Adding New Routes

To add new default routes:

1. Create a new list variable (e.g., `miami_to_cancun_flights`)
2. Add flight dictionaries following the format above
3. Update the `route_map` in `get_default_flights_by_route()`
4. Add the route to `get_all_default_flights()`
5. Add the route to `get_available_routes()`
6. Update this README

## Notes

- All times are in ISO 8601 format
- Prices are realistic estimates and should be updated periodically
- Flight numbers and schedules are fictional but realistic
- The data includes both direct flights and options with layovers
- Each route has at least one flight option to ensure availability
