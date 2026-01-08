from fastapi import FastAPI
from shared.data_types.models import TripRequest, FlightRequest, TransferRequest, StayRequest, HotelSearchRequest, ActivitySearchRequest, SectionType
import asyncio

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Trip Builder Service"}

async def flight_search(request: FlightRequest):
    return {"message": "Flight search"}

async def transfer_search(request: TransferRequest):
    return {"message": "Transfer search"}

async def stay_search(request: StayRequest):
    return {"message": "Stay search"}

async def activity_search(request: ActivitySearchRequest):
    return {"message": "Activity search"}

async def process_sections(request):
    tasks = []
    
    for section in request.sections:
        if section.type == SectionType.FLIGHT:
            tasks.append(flight_search(section.data))
        elif section.type == SectionType.TRANSFER:
            tasks.append(transfer_search(section.data))
        elif section.type == SectionType.STAY:
            tasks.append(stay_search(section.data))
        elif section.type == SectionType.ACTIVITY:
            tasks.append(activity_search(section.data))
    
    # Wait for all searches to complete in parallel
    results = await asyncio.gather(*tasks)
    return results

@app.post("/api/create_trip")
async def create_trip(
    request: TripRequest
):
    request_results = await process_sections(request)

    return {"message": "Trip created successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)