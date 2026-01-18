import sys
import os
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

# 1. Setup path and environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
os.environ["AMADEUS_CLIENT_ID"] = "test_id"
os.environ["AMADEUS_CLIENT_SECRET"] = "test_secret"
os.environ["REDIS_URL"] = "redis://localhost:6379"

# 2. Mock Redis and Amadeus before import
sys.modules['redis'] = MagicMock()
sys.modules['redis.asyncio'] = MagicMock()
mock_amadeus = MagicMock()
sys.modules['amadeus'] = mock_amadeus

from apps.data_collectors.flight_retriever.main import app, generate_unique_flight_id
from shared.data_types.models import FlightSearchRequest

client = TestClient(app)

async def test_flight_caching():
    print("\n--- Testing Flight Retriever Caching & ID System ---")
    
    # Mock Data
    mock_segments = [{
        "carrierCode": "LH",
        "number": "123",
        "departure": {"iataCode": "FRA", "at": "2024-05-01T10:00:00"},
        "arrival": {"iataCode": "JFK", "at": "2024-05-01T13:00:00"}
    }]
    
    mock_offer = {
        "id": "amadeus_offer_1",
        "itineraries": [{"segments": mock_segments, "duration": "PT8H"}],
        "price": {"total": "500.00", "currency": "EUR"},
        "travelerPricings": [{"fareDetailsBySegment": [{"cabin": "ECONOMY"}]}],
        "validatingAirlineCodes": ["LH"]
    }

    # 3. Test ID Generation
    unique_id = generate_unique_flight_id(mock_segments)
    print(f"Generated Unique ID: {unique_id}")
    assert unique_id is not None

    # 4. Mock the API and Cache
    with patch("apps.data_collectors.flight_retriever.main.amadeus") as mock_amadeus_client, \
         patch("apps.data_collectors.flight_retriever.main.cache_get", new_callable=AsyncMock) as mock_cache_get, \
         patch("apps.data_collectors.flight_retriever.main.cache_set", new_callable=AsyncMock) as mock_cache_set, \
         patch("apps.data_collectors.flight_retriever.main.map_provider_id", new_callable=AsyncMock) as mock_map:
        
        # Scenario 1: Search Cache Miss
        mock_amadeus_client.shopping.flight_offers_search.get.return_value.data = [mock_offer]
        mock_amadeus_client.shopping.flight_offers_search.get.return_value.result = {"dictionaries": {"locations": {}}}
        mock_cache_get.return_value = None # Miss everything
        
        search_request = {
            "origin": {"airport_code": "FRA"},
            "destination": {"airport_code": "JFK"},
            "departure_date": "2024-05-01",
            "passengers": 1
        }
        
        print("\nStep 1: First Flight Search (Expecting API Calls)")
        response = client.post("/api/flight_retriever/search", json=search_request)
        assert response.status_code == 200
        data = response.json()
        
        assert data["options"][0]["id"] == unique_id
        print(f" [OK] Flight option given unique_id: {unique_id}")
        
        # Verify mapping and individual caching
        mock_map.assert_called()
        assert mock_cache_set.called
        print(" [OK] Raw offer and transformed data cached")

        # Scenario 2: Second Search (Entire Search Cache Hit)
        print("\nStep 2: Second Search (Expecting Entire Search Cache Hit)")
        mock_amadeus_client.shopping.flight_offers_search.get.reset_mock()
        mock_cache_get.return_value = data # Return previous full response
        
        response2 = client.post("/api/flight_retriever/search", json=search_request)
        assert response2.status_code == 200
        mock_amadeus_client.shopping.flight_offers_search.get.assert_not_called()
        print(" [OK] Search call SKIPPED due to full response cache hit")

        # Scenario 3: Get Details by ID
        print("\nStep 3: Get Flight Details by Unique ID")
        with patch("apps.data_collectors.flight_retriever.main.get_provider_offer", new_callable=AsyncMock) as mock_get_offer:
            mock_get_offer.return_value = mock_offer
            response3 = client.get(f"/api/flight_retriever/flights/{unique_id}")
            assert response3.status_code == 200
            assert response3.json()["id"] == "amadeus_offer_1"
            print(" [OK] Real offer retrieved via Unique ID mapping")

    print("\n--- All Flight Caching Logic Tests Passed ---")

if __name__ == "__main__":
    asyncio.run(test_flight_caching())
