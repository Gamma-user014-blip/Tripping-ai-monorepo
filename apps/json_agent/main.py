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
from typing import List, Dict, Any, Union

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

class TripVariation(BaseModel):
    vibe: str
    trip_request: TripRequest

class JsonAgentResponse(BaseModel):
    variations: List[TripVariation]

class ActionPlan(BaseModel):
    vibe: str
    actions: List[List[Union[str, int, float, None]]]

class ActionPlanResponse(BaseModel):
    plans: List[ActionPlan]


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


def execute_add_flight(args: List[Any]) -> FlightRequest:
    """
    Execute 'FLIGHT' action: Convert positional args to FlightRequest.
    Args protocol: [origin_city, origin_country, origin_code, dest_city, dest_country, dest_code, date, return_date, passengers, cabin]
    """
    # Unpack safely with defaults if list is short (though LLM should be consistent)
    # We expect at least 10 args after the command name
    origin_city = args[0] if len(args) > 0 else ""
    origin_country = args[1] if len(args) > 1 else ""
    origin_code = args[2] if len(args) > 2 else ""
    
    dest_city = args[3] if len(args) > 3 else ""
    dest_country = args[4] if len(args) > 4 else ""
    dest_code = args[5] if len(args) > 5 else ""
    
    date = args[6] if len(args) > 6 else ""
    return_date = args[7] if len(args) > 7 else ""
    # Ensure passengers is int
    try:
        passengers = int(args[8]) if len(args) > 8 else 1
    except:
        passengers = 1
        
    cabin = args[9] if len(args) > 9 else "economy"

    origin = Location(
        city=origin_city,
        country=origin_country,
        airport_code=origin_code
    )
    
    destination = Location(
        city=dest_city,
        country=dest_country,
        airport_code=dest_code
    )
    
    return FlightRequest(
        origin=origin,
        destination=destination,
        departure_date=date,
        return_date=return_date,
        passengers=passengers,
        cabin_class=cabin,
        max_results=20,
        max_stops=2
    )


def execute_add_stay(args: List[Any]) -> StayRequest:
    """
    Execute 'STAY' action: Convert positional args to StayRequest.
    Args protocol: [city, country, start_date, end_date, guests, rooms, description]
    """
    city = args[0] if len(args) > 0 else ""
    country = args[1] if len(args) > 1 else ""
    start_date = args[2] if len(args) > 2 else ""
    end_date = args[3] if len(args) > 3 else ""
    
    try:
        guests = int(args[4]) if len(args) > 4 else 2
    except:
        guests = 2
        
    try:
        rooms = int(args[5]) if len(args) > 5 else 1
    except:
        rooms = 1
        
    description = args[6] if len(args) > 6 else ""

    location = Location(
        city=city,
        country=country
    )
    
    dates = DateRange(
        start_date=start_date,
        end_date=end_date
    )
    
    hotel_request = HotelSearchRequest(
        location=location,
        dates=dates,
        guests=guests,
        rooms=rooms,
        max_results=20,
        min_rating=3.0
    )
    
    activity_request = ActivitySearchRequest(
        location=location,
        dates=dates,
        description=description,
        max_results=10,
        min_rating=3.0
    )
    
    return StayRequest(
        hotel_request=hotel_request,
        activity_request=activity_request
    )


def build_trip_from_actions(actions: List[List[Any]]) -> TripRequest:
    """
    Construct a TripRequest from a list of action arrays.
    """
    sections = []
    
    for action_row in actions:
        if not isinstance(action_row, list) or len(action_row) == 0:
            continue
            
        command = action_row[0]
        # The args are everything after the command
        args = action_row[1:]
        
        if command == "FLIGHT":
            flight_req = execute_add_flight(args)
            sections.append(TripSection(
                type=SectionType.FLIGHT,
                data=flight_req
            ))
            
        elif command == "STAY":
            stay_req = execute_add_stay(args)
            sections.append(TripSection(
                type=SectionType.STAY,
                data=stay_req
            ))
            
    return TripRequest(sections=sections)


def generate_action_sequences(trip_yml: str) -> List[Dict[str, Any]]:
    """
    Generate 3 distinct trip plans (vibes) as sequences of dense tool actions.
    Returns a list of dicts: [{"vibe": "...", "actions": [...]}, ...]
    """
    prompt = f"""
    You are a creative travel planner JSON Agent.
    
    Task:
    Read the trip description and generate 3 DISTINCT trip options (Vibes).
    Each option should have a unique "vibe" (e.g., "Luxury Relax", "Adventure", "Cultural Deep Dive").
    Represent each plan as a "vibe" name and a COMPACT SEQUENCE of actions.
    
    Protocol for Actions:
    
    1. FLIGHT
       Format: ["FLIGHT", origin_city, origin_country, origin_code, dest_city, dest_country, dest_code, date, return_date, passengers, cabin]
       Note: origin_code/dest_code can be empty string if unknown. return_date empty if one-way.
       
    2. STAY
       Format: ["STAY", city, country, start_date, end_date, guests, rooms, description]
       Note: description is a short string of activity preferences.
    
    Rules:
    - Generate EXACTLY 3 options.
    - Ensure logical flow for each option (FLIGHT -> STAY -> FLIGHT).
    - Be consistent with dates.
    - Do not include any additional text or comments.

    Trip Description:
    {trip_yml}
    
    Output JSON Example:
    {{
      "plans": [
        {{
          "vibe": "The Classic Tourist",
          "actions": [
            ["FLIGHT", "NYC", "USA", "JFK", "London", "UK", "LHR", "2024-05-01", "", 1, "economy"],
            ["STAY", "London", "UK", "2024-05-01", "2024-05-05", 1, 1, "Major landmarks and museums"],
            ["FLIGHT", "London", "UK", "LHR", "NYC", "USA", "JFK", "2024-05-05", "", 1, "economy"]
          ]
        }},
        {{
          "vibe": "Hidden Gems",
          "actions": [
            ["FLIGHT", "NYC", "USA", "JFK", "London", "UK", "LHR", "2024-05-01", "", 1, "economy"],
            ["STAY", "London", "UK", "2024-05-01", "2024-05-05", 1, 1, "Local markets and small cafes"],
            ["FLIGHT", "London", "UK", "LHR", "NYC", "USA", "JFK", "2024-05-05", "", 1, "economy"]
          ]
        }},
        {{
          "vibe": "Luxury Living",
          "actions": [
            ["FLIGHT", "NYC", "USA", "JFK", "London", "UK", "LHR", "2024-05-01", "", 1, "first"],
            ["STAY", "London", "UK", "2024-05-01", "2024-05-05", 1, 1, "High-end shopping and fine dining"],
            ["FLIGHT", "London", "UK", "LHR", "NYC", "USA", "JFK", "2024-05-05", "", 1, "first"]
          ]
        }}
      ]
    }}
    """

    response = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "schema": ActionPlanResponse.model_json_schema()
            }
        }
    )

    # Use the structured output directly if possible, or parse the content
    content = response.choices[0].message.content
    print("=== ACTION SEQUENCES ===")
    print(content)
    print("=" * 50)
    
    try:
        # With response_format, content should be valid JSON matching the schema
        data_dict = json.loads(content)
        
        # Convert to list of dicts that existing logic expects: [{"vibe": "...", "actions": [...]}]
        # The schema output is {"plans": [...]}
        if "plans" in data_dict:
            return data_dict["plans"]
        else:
            # Fallback if somehow it's just the list (unlikely with schema)
            return data_dict
            
    except json.JSONDecodeError:
        print("Failed to decode JSON from LLM")
        return []


def create_trip_json_from_yml(trip_yml: str) -> List[TripVariation]:
    """
    Main pipeline: YAML -> Action Sequences (x3) -> List[TripVariation].
    """
    # Step 1: Generate Action Sequences (Returns list of {vibe, actions})
    variations_data = generate_action_sequences(trip_yml)
    
    results = []
    
    # Step 2: Build TripRequest for each variation
    if isinstance(variations_data, list):
        for item in variations_data:
            if not isinstance(item, dict):
                continue
                
            vibe = item.get("vibe", "Standard")
            actions = item.get("actions", [])
            
            if isinstance(actions, list) and len(actions) > 0:
                trip_req = build_trip_from_actions(actions)
                results.append(TripVariation(
                    vibe=vibe,
                    trip_request=trip_req
                ))
    
    # Return results (empty list if failures)
    return results


# ==========================================
# API ENDPOINT
# ==========================================

@app.post("/api/create_json", response_model=JsonAgentResponse)
def create_json(request: JsonAgentRequest):
    if not request.trip_yml or request.trip_yml.strip() == "":
        raise HTTPException(status_code=400, detail="trip_yml cannot be empty")
    
    try:
        variations = create_trip_json_from_yml(request.trip_yml)
        return JsonAgentResponse(variations=variations)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate trip JSON: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)