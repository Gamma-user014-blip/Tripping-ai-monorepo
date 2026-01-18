import sys
# Add the project root to sys.path so 'shared' can be imported without PYTHONPATH hacks

from fastapi import FastAPI, HTTPException, Request
from shared.data_types.models import TripResponse
import uvicorn
from .packages_builder import build_package

app = FastAPI(
    title="Package Builder API",
    description="Optimizes travel packages using shared models.",
    version="2.0.0"
)

@app.post("/api/build-package")
async def create_package(request: Request):
    """
    ### Trip Package Builder
    Accepts a full trip response and selects the best options for each section.
    
    **OPTIMIZED MODE**: 
    - Bypasses FastAPI's automatic request/response validation
    - Uses Pydantic V2's fast model_validate for manual parsing
    - Returns raw dicts to skip response validation overhead
    """
    try:
        
        # Parse JSON without FastAPI's automatic validation (trusted data)
        raw_data = await request.json()
        
        # Use model_validate which properly constructs nested models
        # In Pydantic V2 this is already very fast
        trip = TripResponse.model_validate(raw_data)
        
        
        # Run business logic
        result = build_package(trip)
        
        
        # Convert result to dictionaries without validation
        # Using model_dump with mode='python' for fastest serialization
        response_data = result.model_dump(mode='python')
        
        

        
        return response_data
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] {error_details}")
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Disable access logs for a slight performance boost
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
