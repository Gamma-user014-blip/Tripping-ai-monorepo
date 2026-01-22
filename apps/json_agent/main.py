from fastapi import FastAPI, HTTPException
from shared.data_types.models import (
    TripRequest, TripSection, SectionType,
    FlightRequest, StayRequest, Location, DateRange,
    HotelSearchRequest, ActivitySearchRequest
)
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel
from openai import OpenAI
import json
import os
import re
from typing import List, Dict, Any

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

client = OpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai"
)

app = FastAPI()

# ==========================================
# API MODELS
# ==========================================

class JsonAgentRequest(BaseModel):
    trip_yml: str = ""

class JsonAgentResponse(BaseModel):
    trip_json: TripRequest


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def _strip_markdown_and_clean_json(text: str) -> str:
    """
    Robustly extract the largest JSON object or array from the text,
    ignoring any markdown code blocks or surrounding text.
    """
    text = text.strip()
    
    # Find the start of the JSON structure
    first_brace = text.find('{')
    first_bracket = text.find('[')
    
    if first_brace == -1 and first_bracket == -1:
        return text
        
    # Determine start and expected end based on which opening char appears first
    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        start_idx = first_brace
        end_char = '}'
    else:
        start_idx = first_bracket
        end_char = ']'
        
    # Slice from the start
    text = text[start_idx:]
    
    # Find the last occurrence of the corresponding closing character
    last_idx = text.rfind(end_char)
    
    if last_idx != -1:
        text = text[:last_idx+1]
        
    return text


def execute_add_flight(args: Dict[str, Any]) -> FlightRequest:
    """
    Execute 'add_flight' action: Convert flat args to FlightRequest model.
    """
    origin = Location(
        city=args.get("origin_city", ""),
        country=args.get("origin_country", ""),
        airport_code=args.get("origin_airport_code", "")
    )
    
    destination = Location(
        city=args.get("destination_city", ""),
        country=args.get("destination_country", ""),
        airport_code=args.get("destination_airport_code", "")
    )
    
    return FlightRequest(
        origin=origin,
        destination=destination,
        departure_date=args.get("date", ""),
        # If 'return_date' is in args, use it, else default empty
        return_date=args.get("return_date", ""),
        passengers=args.get("passengers", 1),
        cabin_class=args.get("cabin_class", "economy"),
        max_results=20,
        max_stops=2
    )


def execute_add_stay(args: Dict[str, Any]) -> StayRequest:
    """
    Execute 'add_stay' action: Convert flat args to StayRequest model.
    """
    location = Location(
        city=args.get("city", ""),
        country=args.get("country", "")
    )
    
    # Calculate end_date from start_date + nights if needed
    # For now, we trust the LLM to give us valid dates or we accept empty strings if missing
    # In a real app, date math libraries like datetime would be used here.
    
    dates = DateRange(
        start_date=args.get("start_date", ""),
        end_date=args.get("end_date", "") # Expecting LLM to provide end_date or we leave it empty
    )
    
    hotel_request = HotelSearchRequest(
        location=location,
        dates=dates,
        guests=args.get("guests", 2),
        rooms=args.get("rooms", 1),
        max_results=20,
        min_rating=3.0,
        # 'preferences' could be mapped to amenity lists or descriptions
    )
    
    activity_request = ActivitySearchRequest(
        location=location,
        dates=dates,
        description=args.get("activity_preferences", ""),
        max_results=10,
        min_rating=3.0
    )
    
    return StayRequest(
        hotel_request=hotel_request,
        activity_request=activity_request
    )


def build_trip_from_actions(actions: List[Dict[str, Any]]) -> TripRequest:
    """
    Construct a TripRequest from a list of action dictionaries.
    """
    sections = []
    
    for action_item in actions:
        action_name = action_item.get("action")
        args = action_item.get("args", {})
        
        if action_name == "add_flight":
            flight_req = execute_add_flight(args)
            sections.append(TripSection(
                type=SectionType.FLIGHT,
                data=flight_req
            ))
            
        elif action_name == "add_stay":
            stay_req = execute_add_stay(args)
            sections.append(TripSection(
                type=SectionType.STAY,
                data=stay_req
            ))
            
    return TripRequest(sections=sections)


def generate_action_sequences(trip_yml: str) -> List[Dict[str, Any]]:
    """
    Generate one trip plan as a sequence of tool actions.
    """
    prompt = f"""
    You are a creative travel planner JSON Agent.
    
    Task:
    Read the trip description and generate a CREATIVE trip plan.
    Represent the plan as a sequence of ACTIONS.
    
    Available Actions:
    1. add_flight
       Args: origin_city, origin_country, origin_airport_code (opt), destination_city, destination_country, destination_airport_code (opt), date (YYYY-MM-DD), return_date (opt, YYYY-MM-DD), passengers, cabin_class
    
    2. add_stay
       Args: city, country, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), guests, rooms, activity_preferences (string description of what to do)
    
    Rules:
    - Return a JSON List of action objects: {{ "action": "name", "args": {{ ... }} }}
    - Ensure logical flow (flight -> stay -> flight).
    - Be consistent with dates.
    - Be creative with the plan.
    - Do not include any additional text or comments.

    Trip Description:
    {trip_yml}
    
    Output JSON Format:
    [
      {{ "action": "add_flight", "args": {{ ... }} }},
      {{ "action": "add_stay", "args": {{ ... }} }},
      ...
    ]
    """

    response = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )

    cleaned_text = _strip_markdown_and_clean_json(response.choices[0].message.content)
    print("=== ACTION SEQUENCE ===")
    print(cleaned_text)
    print("=" * 50)
    
    try:
        data = json.loads(cleaned_text)
        # Validate it's a list
        if not isinstance(data, list):
            return []
        return data
    except json.JSONDecodeError:
        print("Failed to decode JSON from LLM")
        return []


def create_trip_json_from_yml(trip_yml: str) -> TripRequest:
    """
    Main pipeline: YAML -> Actions -> Single TripRequest.
    """
    # Step 1: Generate Action Sequence
    actions = generate_action_sequences(trip_yml)
    
    # Step 2: Build TripRequest from actions
    if isinstance(actions, list) and len(actions) > 0:
        return build_trip_from_actions(actions)
    
    # Return empty request if something failed
    return TripRequest(sections=[])


# ==========================================
# API ENDPOINT
# ==========================================

@app.post("/api/create_json", response_model=JsonAgentResponse)
def create_json(request: JsonAgentRequest):
    if not request.trip_yml or request.trip_yml.strip() == "":
        raise HTTPException(status_code=400, detail="trip_yml cannot be empty")
    
    try:
        result = create_trip_json_from_yml(request.trip_yml)
        return JsonAgentResponse(trip_json=result)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate trip JSON: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)