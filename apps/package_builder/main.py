from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Any
from pydantic import BaseModel
import uvicorn
from packages_builder import build_package

app = FastAPI(
    title="Package Builder API",
    description="Optimizes a sequence of travel options.",
    version="1.6.0"
)

# Simple model to keep the documentation clean and focused on the core structure
class TripStage(BaseModel):
    type: str
    options: List[Dict[str, Any]]

# Minimal exampl
minimal_example = [
    {
        "type": "flight",
        "options": [
            {"id": "flight_1", "...": "..."}
        ]
    },
    {
        "type": "hotel",
        "options": [
            {"id": "hotel_1", "...": "..."}
        ]
    }
]

@app.post("/build-package")
async def create_package(
    stages: List[TripStage] = Body(..., example=minimal_example)
):
    """
    ### Optimized Package Builder
    Input is a list of stages. Each stage defines its type and available options.
    """
    try:
        # Convert models to raw dicts for the builder
        raw_stages = [stage.model_dump() for stage in stages]
        return build_package(raw_stages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=81)
