from fastapi import FastAPI
from shared.data_types.models import *
import os
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()

app = FastAPI()

HOTEL_REQUEST_API = os.getenv("HOTEL_REQUEST_API", "http://localhost:8000/api/hotels/search")
FLIGHT_REQUEST_API = os.getenv("FLIGHT_REQUEST_API", "http://localhost:8000/api/flights/search")
TRANSFER_REQUEST_API = os.getenv("TRANSFER_REQUEST_API", "http://localhost:8000/api/transport/search")
ACTIVITY_REQUEST_API = os.getenv("ACTIVITY_REQUEST_API", "http://localhost:8000/api/activities/search")
PACKAGE_BUILDER_API = os.getenv("PACKAGE_BUILDER_API", "http://localhost:8000/api/build-package")

@app.get("/")
def read_root():
    return {"message": "Trip Builder Service"}

async def flight_search(request: FlightRequest, client: httpx.AsyncClient) -> FlightResponse:
    try:
        response = await client.post(FLIGHT_REQUEST_API, json=request.model_dump())
        response.raise_for_status()
        return FlightResponse.model_validate(response.json())
    except Exception as e:
        print(f"Flight search failed: {type(e).__name__}: {e}")
        return FlightResponse()

async def transfer_search(request: TransferRequest, client: httpx.AsyncClient) -> TransferResponse:
    try:
        response = await client.post(TRANSFER_REQUEST_API, json=request.model_dump())
        response.raise_for_status()
        return TransferResponse.model_validate(response.json())
    except Exception as e:
        print(f"Transfer search failed: {type(e).__name__}: {e}")
        return TransferResponse()

async def stay_search(request: StayRequest, client: httpx.AsyncClient) -> StayResponse:
    # Execute hotel and activity searches in parallel
    
    async def get_hotels():
        try:
            res = await client.post(HOTEL_REQUEST_API, json=request.hotel_request.model_dump())
            res.raise_for_status()
            return HotelSearchResponse.model_validate(res.json())
        except Exception as e:
            print(f"Hotel search failed: {type(e).__name__}: {e}")
            return HotelSearchResponse()

    async def get_activities():
        try:
            res = await client.post(ACTIVITY_REQUEST_API, json=request.activity_request.model_dump())
            res.raise_for_status()
            data = res.json()
            result = ActivitySearchResponse.model_validate(data)
            print(f"Activity search returned {len(result.options)} activities")
            return result
        except Exception as e:
            print(f"Activity search failed: {type(e).__name__}: {repr(e)}")
            return ActivitySearchResponse()

    hotel_data, activity_data = await asyncio.gather(get_hotels(), get_activities())
    
    return StayResponse(
        hotel_options=hotel_data.options,
        activity_options=activity_data.options
    )

async def process_sections(request: TripRequest) -> TripResponse:
    trip_response = TripResponse()
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        # Helper to process a single section and wrap it
        async def process_section(section: TripSection) -> TripSectionResponse:
            if section.type == SectionType.FLIGHT:
                data = await flight_search(section.data, client)
                return TripSectionResponse(type=SectionType.FLIGHT, data=data)
            
            elif section.type == SectionType.TRANSFER:
                data = await transfer_search(section.data, client)
                return TripSectionResponse(type=SectionType.TRANSFER, data=data)
            
            elif section.type == SectionType.STAY:
                data = await stay_search(section.data, client)
                return TripSectionResponse(type=SectionType.STAY, data=data)
            
            # Fallback for unknown types if needed, or raise
            print(f"DEBUG: process_section returning None for unknown section type: {section.type}")
            return None

        # Create tasks for all sections
        coros = [process_section(section) for section in request.sections]
        
        # Execute all in parallel
        results = await asyncio.gather(*coros)
        
        # Filter out Nones if any
        trip_response.sections = [r for r in results if r]
            
    return trip_response

async def build_package(trip_response: TripResponse) -> FinalTripLayout:
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        res = await client.post(PACKAGE_BUILDER_API, json=trip_response.model_dump())
        res.raise_for_status()
        return FinalTripLayout.model_validate(res.json())

@app.post("/api/create_trip", response_model=FinalTripLayout)
async def create_trip(
    request: TripRequest
):
    print(f"Received create_trip request with {len(request.sections)} sections")
    trip_response = await process_sections(request)
    print(f"Processed sections, got {len(trip_response.sections)} responses")
    
    print("Calling package builder...")
    package = await build_package(trip_response)
    print("Package builder returned")
    
    # Inject images back from search results into final package
    hotel_images = {
        h.id: h.image 
        for s in trip_response.sections 
        if s.type == SectionType.STAY 
        for h in s.data.hotel_options 
        if h.image
    }
    
    for section in package.sections:
        if section.type == SectionType.STAY and section.data.hotel.id in hotel_images:
            section.data.hotel.image = hotel_images[section.data.hotel.id]
      
    return package


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)