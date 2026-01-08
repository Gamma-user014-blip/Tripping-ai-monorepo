import sys
import os
# Add the project root to sys.path so 'shared' can be imported without PYTHONPATH hacks
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from shared.data_types.models import TripResponse
import uvicorn
import time
from packages_builder import build_package

app = FastAPI(
    title="Package Builder API",
    description="Optimizes travel packages using shared models.",
    version="2.0.0"
)

@app.post("/build-package")
async def create_package(trip: TripResponse):
    """
    ### Trip Package Builder
    Accepts a full trip response and selects the best options for each section.
    """
    try:
        start_time = time.time()
        result = build_package(trip)
        end_time = time.time()
        
        print(f"[PERF] Package built in {(end_time - start_time) * 1000:.2f}ms")
        sys.stdout.flush()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Disable access logs for a slight performance boost
    uvicorn.run(app, host="127.0.0.1", port=81, access_log=False)
