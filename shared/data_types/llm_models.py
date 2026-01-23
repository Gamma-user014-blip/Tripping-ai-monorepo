from typing import List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class FillStatus(str, Enum):
    ready = "ready"
    needs_more_info = "needs_more_info"
    error = "error"


class UpdateTripRequest(BaseModel):
    raw_user_message: str = Field(..., description="The raw user message to use for updating the trip YAML.")
    current_yaml_state: str = Field(default="", description="The current YAML state, or empty string for fresh start.")

class ReadyResponse(BaseModel):
    user_details: str = Field(..., description="The filled/updated YAML output.")

class FillResponse(BaseModel):
    yaml: str = Field(..., description="The filled/updated YAML output.")
    status: FillStatus = Field(..., description="Whether the YAML is ready or needs more info.")
    message: Optional[str] = Field(None, description="Optional explanation or follow-up question if not ready.")