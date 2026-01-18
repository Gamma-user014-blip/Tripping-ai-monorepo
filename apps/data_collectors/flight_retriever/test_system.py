import sys
import os
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

# 1. Setup path and environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
os.environ["AMADEUS_CLIENT_ID"] = "test_id"
os.environ["AMADEUS_CLIENT_SECRET"] = "test_secret"
os.environ["REDIS_URL"] = "redis://localhost:6379"

# 2. Mock Redis and Amadeus before import to avoid real connections
sys.modules['redis'] = MagicMock()
sys.modules['redis.asyncio'] = MagicMock()
mock_amadeus_module = MagicMock()
sys.modules['amadeus'] = mock_amadeus_module

# Import app and needed functions after mocking
from apps.data_collectors.flight_retriever.main import app, generate_unique_flight_id
from shared.data_types.models import FlightOption, FlightSearchResponse

client = TestClient(app)

async def test_flight_retriever_logic_and_caching():
    print("\n--- Starting Detailed Flight Retriever System Test ---")
    
    # Define a realistic mock offer from Amadeus
    mock_segments = [
        {
            "departure": {"iataCode": "LHR", "at": "2024-06-01T10:00:00", "terminal": "5"},
            "arrival": {"iataCode": "JFK", "at": "2024-06-01T13:00:00", "terminal": "4"},
            "carrierCode": "BA",
            "number": "117",
            "aircraft": {"code": "777"},
            "duration": "PT8H",
            "id": "1"
        }
    ]
    
    mock_offer = {
        "id": "amadeus_original_id_123",
        "itineraries": [
            {
                "duration": "PT8H",
                "segments": mock_segments
            }
        ],
        "price": {
            "total": "650.50",
            "currency": "GBP",
            "grandTotal": "650.50"
        },
        "travelerPricings": [
            {
                "travelerId": "1",
                "fareOption": "STANDARD",
                "price": {"total": "650.50", "currency": "GBP"},
                "fareDetailsBySegment": [
                    {
                        "segmentId": "1",
                        "cabin": "ECONOMY",
                        "amenities": [
                            {"description": "WI-FI", "isFree": True},
                            {"description": "MEAL", "isFree": True}
                        ],
                        "includedCheckedBags": {"quantity": 1}
                    }
                ]
            }
        ],
        "validatingAirlineCodes": ["BA"]
    }

    # 3. Verify Deterministic ID Generation
    expected_unique_id = generate_unique_flight_id(mock_segments)
    print(f"Generated System ID: {expected_unique_id}")
    
    # Assert id is consistent
    assert expected_unique_id == generate_unique_flight_id(mock_segments)
    assert "-" in expected_unique_id # UUID format check
    print(" [PASS] Unique ID generation is deterministic and correctly formatted.")

    # 4. Mock the API and Cache behavior
    with patch("apps.data_collectors.flight_retriever.main.amadeus") as mock_api_client, \
         patch("apps.data_collectors.flight_retriever.main.cache_get", new_callable=AsyncMock) as mock_get, \
         patch("apps.data_collectors.flight_retriever.main.cache_set", new_callable=AsyncMock) as mock_set, \
         patch("apps.data_collectors.flight_retriever.main.map_provider_id", new_callable=AsyncMock) as mock_map:
        
        # --- PHASE 1: CACHE MISS (Fresh Data) ---
        print("\nStep 1: First search (Cache Miss)")
        mock_api_client.shopping.flight_offers_search.get.return_value.data = [mock_offer]
        mock_api_client.shopping.flight_offers_search.get.return_value.result = {
            "dictionaries": {
                "locations": {
                    "LHR": {"cityName": "London", "countryCode": "GB"},
                    "JFK": {"cityName": "New York", "countryCode": "US"}
                }
            }
        }
        mock_get.return_value = None # Force cache miss
        
        search_req = {
            "origin": {"airport_code": "LHR"},
            "destination": {"airport_code": "JFK"},
            "departure_date": "2024-06-01",
            "passengers": 1
        }
        
        response = client.post("/api/flight_retriever/search", json=search_req)
        assert response.status_code == 200
        data = response.json()
        
        # Verify result quality
        assert len(data["options"]) == 1
        option = data["options"][0]
        
        print(" Validating Transformed Data Content:")
        assert option["id"] == expected_unique_id
        assert option["total_price"]["amount"] == 650.50
        assert option["total_price"]["currency"] == "GBP"
        assert option["outbound"]["airline"] == "BA"
        assert option["outbound"]["cabin_class"] == "economy"
        assert option["outbound"]["amenities"]["wifi"] is True
        assert option["outbound"]["luggage"]["checked_bags"] == 1
        assert option["outbound"]["origin"]["airport_code"] == "LHR"
        assert option["outbound"]["origin"]["city"] == "London"
        
        print("  [OK] Data transformation is accurate and reasonably parsed.")

        # Verify Caching calls
        # Expected: 1 set for full search, 1 for individual option, 1 for id mapping
        assert mock_set.called
        assert mock_map.called
        print("  [OK] Caching and ID mapping triggered correctly.")

        # --- PHASE 2: CACHE HIT (Retrieval) ---
        print("\nStep 2: Second search (Cache Hit)")
        mock_api_client.shopping.flight_offers_search.get.reset_mock()
        
        # Simulate cache returning the full search response
        mock_get.return_value = data 
        
        response2 = client.post("/api/flight_retriever/search", json=search_req)
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert data2["options"][0]["id"] == expected_unique_id
        mock_api_client.shopping.flight_offers_search.get.assert_not_called()
        print("  [OK] Search call SKIPPED. System retrieved full response from cache.")

        # --- PHASE 3: PROVIDER MAPPING (Persistence) ---
        print("\nStep 3: Verifying Unique ID -> Provider Data Mapping")
        with patch("apps.data_collectors.flight_retriever.main.get_provider_offer", new_callable=AsyncMock) as mock_get_offer:
            mock_get_offer.return_value = mock_offer
            
            response3 = client.get(f"/api/flight_retriever/flights/{expected_unique_id}")
            assert response3.status_code == 200
            details = response3.json()
            
            # This should be the ORIGINAL Amadeus offer data
            assert details["id"] == "amadeus_original_id_123"
            assert details["validatingAirlineCodes"] == ["BA"]
            print("  [OK] Resolved UNIQUE_ID back to original PROVIDER_DATA correctly.")

    print("\n--- All System Tests Passed Successfully ---")

if __name__ == "__main__":
    asyncio.run(test_flight_retriever_logic_and_caching())
