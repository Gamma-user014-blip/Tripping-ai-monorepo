#!/usr/bin/env python3
"""
Test script for default_flights.py
Run this to verify the default flights data is working correctly
"""

import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_types.default_flights import (
    get_default_flights_by_route,
    get_all_default_flights,
    get_default_flight_by_id,
    get_available_routes
)


def test_get_flights_by_route():
    print("=" * 60)
    print("TEST: Get flights by route")
    print("=" * 60)
    
    # Test valid route
    flights = get_default_flights_by_route("New York", "London")
    print(f"\n✓ New York → London: {len(flights)} flights found")
    for flight in flights:
        print(f"  - {flight['outbound']['airline']} {flight['outbound']['flight_number']}: "
              f"${flight['price_per_person']['amount']:.2f} per person")
    
    # Test case insensitivity
    flights2 = get_default_flights_by_route("new york", "LONDON")
    assert len(flights) == len(flights2), "Case insensitivity test failed"
    print(f"\n✓ Case insensitivity works: {len(flights2)} flights")
    
    # Test invalid route
    flights3 = get_default_flights_by_route("Mars", "Venus")
    print(f"\n✓ Invalid route returns empty list: {len(flights3)} flights")
    
    print("\n✅ Route lookup tests passed!\n")


def test_get_all_flights():
    print("=" * 60)
    print("TEST: Get all default flights")
    print("=" * 60)
    
    all_flights = get_all_default_flights()
    print(f"\n✓ Total flights available: {len(all_flights)}")
    
    # Verify all have required fields
    for flight in all_flights:
        assert "id" in flight, f"Missing 'id' in flight"
        assert "outbound" in flight, f"Missing 'outbound' in flight {flight['id']}"
        assert "total_price" in flight, f"Missing 'total_price' in flight {flight['id']}"
        assert "airline" in flight["outbound"], f"Missing 'airline' in flight {flight['id']}"
    
    print("✓ All flights have required fields")
    
    # Check for unique IDs
    ids = [f["id"] for f in all_flights]
    assert len(ids) == len(set(ids)), "Duplicate flight IDs found!"
    print("✓ All flight IDs are unique")
    
    print("\n✅ All flights tests passed!\n")


def test_get_flight_by_id():
    print("=" * 60)
    print("TEST: Get flight by ID")
    print("=" * 60)
    
    # Test valid ID
    flight = get_default_flight_by_id("default_f_ny_ldn_1")
    assert flight is not None, "Failed to find flight by ID"
    print(f"\n✓ Found flight: {flight['outbound']['airline']} {flight['outbound']['flight_number']}")
    print(f"  Route: {flight['outbound']['origin']['city']} → "
          f"{flight['outbound']['destination']['city']}")
    
    # Test invalid ID
    flight2 = get_default_flight_by_id("nonexistent_flight")
    assert flight2 is None, "Should return None for invalid ID"
    print("✓ Invalid ID returns None")
    
    print("\n✅ Flight ID lookup tests passed!\n")


def test_available_routes():
    print("=" * 60)
    print("TEST: Get available routes")
    print("=" * 60)
    
    routes = get_available_routes()
    print(f"\n✓ Available routes: {len(routes)}")
    for origin, destination in routes:
        print(f"  - {origin} → {destination}")
    
    # Verify each route has flights
    for origin, destination in routes:
        flights = get_default_flights_by_route(origin, destination)
        assert len(flights) > 0, f"No flights found for {origin} → {destination}"
    
    print("\n✓ All routes have at least one flight")
    print("\n✅ Available routes tests passed!\n")


def test_data_structure():
    print("=" * 60)
    print("TEST: Validate data structure")
    print("=" * 60)
    
    flight = get_default_flight_by_id("default_f_ny_ldn_1")
    
    # Check outbound structure
    outbound = flight["outbound"]
    required_outbound_fields = [
        "origin", "destination", "departure_time", "arrival_time",
        "duration_minutes", "stops", "layovers", "airline", "flight_number",
        "aircraft", "cabin_class", "amenities", "luggage"
    ]
    
    for field in required_outbound_fields:
        assert field in outbound, f"Missing field '{field}' in outbound"
    
    print("✓ Outbound segment has all required fields")
    
    # Check location structure
    origin = outbound["origin"]
    required_location_fields = ["city", "country", "airport_code", "latitude", "longitude"]
    for field in required_location_fields:
        assert field in origin, f"Missing field '{field}' in location"
    
    print("✓ Location has all required fields")
    
    # Check amenities structure
    amenities = outbound["amenities"]
    required_amenity_fields = ["wifi", "meal", "entertainment", "power_outlet", "legroom_inches"]
    for field in required_amenity_fields:
        assert field in amenities, f"Missing field '{field}' in amenities"
    
    print("✓ Amenities has all required fields")
    
    # Check luggage structure
    luggage = outbound["luggage"]
    required_luggage_fields = [
        "checked_bags", "checked_bag_weight_kg", "carry_on_bags",
        "carry_on_weight_kg", "carry_on_dimensions_cm"
    ]
    for field in required_luggage_fields:
        assert field in luggage, f"Missing field '{field}' in luggage"
    
    print("✓ Luggage has all required fields")
    
    # Check price structure
    assert "currency" in flight["total_price"], "Missing 'currency' in total_price"
    assert "amount" in flight["total_price"], "Missing 'amount' in total_price"
    print("✓ Price has all required fields")
    
    # Check scores structure
    scores = flight["scores"]
    required_score_fields = ["price_score", "quality_score", "convenience_score", "preference_score"]
    for field in required_score_fields:
        assert field in scores, f"Missing field '{field}' in scores"
    
    print("✓ Scores has all required fields")
    
    print("\n✅ Data structure validation passed!\n")


def main():
    print("\n" + "=" * 60)
    print("DEFAULT FLIGHTS TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_get_flights_by_route()
        test_get_all_flights()
        test_get_flight_by_id()
        test_available_routes()
        test_data_structure()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\nThe default flights data is ready to use!")
        print("See DEFAULT_FLIGHTS_README.md for usage instructions.\n")
        
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
