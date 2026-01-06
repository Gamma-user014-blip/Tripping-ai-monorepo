from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import time
import uvicorn
from packages_builder import build_package

app = FastAPI()

class Packet(BaseModel):
    entry_flights: List[Dict[str, Any]]
    list_of_hotels: List[List[Dict[str, Any]]]
    exit_flights: List[Dict[str, Any]]

@app.post("/build-package")
async def create_package(packet: Packet):
    try:
        # Benchmarking
        start_time = time.time()
        
        # Convert Pydantic model to dict for existing logic
        packet_dict = packet.model_dump()
        result = build_package(packet_dict)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        print(f"Package built in {duration_ms:.2f} ms")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=81)
