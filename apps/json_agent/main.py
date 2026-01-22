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

class GeneratePlansRequest(BaseModel):
    trip_yml: str = ""

class GeneratedTripResponse(BaseModel):
    vibe: str
    trip_request: TripRequest

class TripPlan(BaseModel):
    vibe: str
    actions: List[List[Union[str, int, float, None]]]

class TripPlansResponse(BaseModel):
    plans: List[TripPlan]

class GenerateTripRequest(BaseModel):
    vibe: str
    actions: List[List[Union[str, int, float, None]]]

class EditTripPlansRequest(BaseModel):
    plans: List[TripPlan]
    user_text: str

class EditTripPlansResponse(BaseModel):
    plans: List[TripPlan]
    modified_indices: List[int]


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def extract_json_from_text(text: str) -> str:
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


def parse_flight_action(args: List[Any]) -> FlightRequest:
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


def parse_stay_action(args: List[Any]) -> StayRequest:
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


def build_trip_request_from_instructions(actions: List[List[Any]]) -> TripRequest:
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
            flight_req = parse_flight_action(args)
            sections.append(TripSection(
                type=SectionType.FLIGHT,
                data=flight_req
            ))
            
        elif command == "STAY":
            stay_req = parse_stay_action(args)
            sections.append(TripSection(
                type=SectionType.STAY,
                data=stay_req
            ))
            
    return TripRequest(sections=sections)


def generate_trip_plans_from_text(trip_yml: str) -> List[Dict[str, Any]]:
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
                "schema": TripPlansResponse.model_json_schema()
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


def calculate_modified_indices(original_plans: List[TripPlan], edited_plans: List[TripPlan]) -> List[int]:
    """
    Compare two lists of TripPlans and return the indices of modified ones.
    """
    modified_indices = []
    
    # We assume the lists have the same length for simplicity in comparison mapping
    # If the LLM changed the order or length, this logic might need to be more complex
    # but for a direct "edit these plans" task, the mapping is usually 1:1.
    for i, (orig, edited) in enumerate(zip(original_plans, edited_plans)):
        # Convert models to dict for comparison
        if orig.model_dump() != edited.model_dump():
            modified_indices.append(i)
            
    # Handle cases where lengths differ
    if len(edited_plans) > len(original_plans):
        for i in range(len(original_plans), len(edited_plans)):
            modified_indices.append(i)
            
    return modified_indices


def edit_trip_plans_with_llm(plans: List[TripPlan], user_text: str) -> List[TripPlan]:
    """
    Use LLM to apply changes to a list of TripPlans based on natural language instructions.
    """
    plans_json = json.dumps([p.model_dump() for p in plans], indent=2)
    
    prompt = f"""
    You are an expert travel coordinator. 
    You are given a list of travel plans in JSON format and specific instructions for editing them.
    
    Current Plans:
    {plans_json}
    
    Instructions:
    {user_text}
    
    Protocol for Actions:
    1. FLIGHT: ["FLIGHT", origin_city, origin_country, origin_code, dest_city, dest_country, dest_code, date, return_date, passengers, cabin]
       - The 'date' is the day of travel.
    2. STAY: ["STAY", city, country, start_date, end_date, guests, rooms, description]
       - 'start_date' is check-in, 'end_date' is check-out.
    
    Constraint & Logic Rules:
    - DATE ARITHMETIC: If a user asks to "shorten X by 1 day and give it to Y", this refers to the transition date BETWEEN X and Y.
      Example: If X is [2026-09-13 to 2026-09-17] and Y is [2026-09-17 to 2026-09-20], and the user says "shorten X by one day and give it to Y":
      * New X: [2026-09-13 to 2026-09-16]
      * New Y: [2026-09-16 to 2026-09-20]
      * The FLIGHT between X and Y must move from 2026-09-17 to 2026-09-16.
    - PHRASING: Interpret "shorten in one day" as "shorten by one day" (duration - 1).
    - CONTIGUITY: Stays and flights must remain contiguous. A check-out date for one city should generally match the check-in date for the next city and the flight date between them.
    - SPECIFICITY: Only modify the specific plan(s) mentioned (e.g., "first option"). Leave others UNCHANGED.
    - VISUAL INTEGRITY: Do not modify the JSON structure or the "vibe" name unless explicitly asked.
    
    Return the FULL updated list of plans in the specified output format.
    """
    
    response = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "schema": TripPlansResponse.model_json_schema()
            }
        }
    )
    
    content = response.choices[0].message.content
    try:
        data_dict = json.loads(content)
        if "plans" in data_dict:
            return [TripPlan(**p) for p in data_dict["plans"]]
        return []
    except Exception as e:
        print(f"Error parsing edited plans: {str(e)}")
        return []


# ==========================================
# API ENDPOINT
# ==========================================

@app.post("/api/generate-plans", response_model=TripPlansResponse)
def generate_plans(request: GeneratePlansRequest):
    if not request.trip_yml or request.trip_yml.strip() == "":
        raise HTTPException(status_code=400, detail="trip_yml cannot be empty")
    
    try:
        variations_data = generate_trip_plans_from_text(request.trip_yml)
        
        plans = []
        if isinstance(variations_data, list):
            for item in variations_data:
                if isinstance(item, dict):
                    vibe = item.get("vibe", "Standard")
                    actions = item.get("actions", [])
                    plans.append(TripPlan(vibe=vibe, actions=actions))
                    
        return TripPlansResponse(plans=plans)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate trip plans: {str(e)}")


@app.post("/api/build-trip-request", response_model=GeneratedTripResponse)
def build_trip_request(request: GenerateTripRequest):
    try:
        trip_req = build_trip_request_from_instructions(request.actions)
        return GeneratedTripResponse(
            vibe=request.vibe,
            trip_request=trip_req
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to build trip: {str(e)}")


@app.post("/api/edit-plans", response_model=EditTripPlansResponse)
def edit_plans(request: EditTripPlansRequest):
    if not request.user_text or request.user_text.strip() == "":
        raise HTTPException(status_code=400, detail="user_text cannot be empty")
    
    try:
        edited_plans = edit_trip_plans_with_llm(request.plans, request.user_text)
        
        if not edited_plans:
             raise HTTPException(status_code=500, detail="Failed to edit plans via LLM")
             
        modified_indices = calculate_modified_indices(request.plans, edited_plans)
        
        return EditTripPlansResponse(
            plans=edited_plans,
            modified_indices=modified_indices
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to edit trip plans: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)