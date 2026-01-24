from fastapi import FastAPI, HTTPException, Request
import logging
import time
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
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Union, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

client = OpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai"
)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Handled {request.method} {request.url.path} in {duration:.4f} seconds")
    return response

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

def _normalize_country_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _load_country_name_to_code_map() -> Dict[str, str]:
    try:
        repo_root = Path(__file__).resolve().parents[2]
        shared_countries_path = (
            repo_root / "shared" / "metadata" / "countries.json"
        )
        legacy_web_countries_path = (
            repo_root / "apps" / "web-client" / "common" / "countries.json"
        )

        countries_path = (
            shared_countries_path
            if shared_countries_path.exists()
            else legacy_web_countries_path
        )

        raw = countries_path.read_text(encoding="utf-8")
        items = json.loads(raw)
        if not isinstance(items, list):
            return {}

        mapping: Dict[str, str] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            code = item.get("code")
            if not isinstance(name, str) or not isinstance(code, str):
                continue
            name = name.strip()
            code = code.strip()
            if not name or not code:
                continue
            mapping[_normalize_country_key(name)] = code.upper()
        return mapping
    except Exception:
        return {}


_COUNTRY_NAME_TO_ISO2: Dict[str, str] = _load_country_name_to_code_map()


def normalize_country_to_iso2(country: str) -> str:
    if not isinstance(country, str):
        return ""

    country = country.strip()
    if not country:
        return country

    if re.fullmatch(r"[A-Za-z]{2}", country):
        return country.upper()

    key = _normalize_country_key(country)
    code = _COUNTRY_NAME_TO_ISO2.get(key)
    if code:
        return code

    return country

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
    except Exception:
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
        max_results=10,
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
    except Exception:
        guests = 2
        
    try:
        rooms = int(args[5]) if len(args) > 5 else 1
    except Exception:
        rooms = 1
        
    description = args[6] if len(args) > 6 else ""

    location = Location(
        city=city,
        country=normalize_country_to_iso2(country)
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
        max_results=10,
        min_rating=3.0
    )
    
    activity_request = ActivitySearchRequest(
        location=location,
        dates=dates,
        description=description,
        max_results=3,
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


def _normalize_route_city(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", value).strip().lower()


def _extract_route_signature(plan: Dict[str, Any]) -> List[str]:
    actions = plan.get("actions")
    if not isinstance(actions, list):
        return []

    signature: List[str] = []
    for action in actions:
        if not isinstance(action, list) or len(action) < 2:
            continue
        if action[0] != "STAY":
            continue
        city = _normalize_route_city(action[1])
        if city:
            signature.append(city)
    return signature


def _route_signature_key(signature: List[str]) -> str:
    return ">".join(signature)


def generate_single_trip_plan(
    trip_yml: str,
    previous_vibes: List[str],
    forbidden_route_signatures: List[List[str]],
    diversity_directive: str,
) -> Dict[str, Any]:
    """
    Generate a single trip plan (vibe) as a sequence of dense tool actions.
    Ensures the vibe is distinct from previous_vibes and the city route differs.
    """
    vibe_context = ""
    if previous_vibes:
        vibe_context = f"Avoid these previous vibes: {', '.join(previous_vibes)}."

    forbidden_routes_json = json.dumps(forbidden_route_signatures)

    prompt = f"""
    You are a creative travel planner JSON Agent.
    
    Task:
    Read the trip description and generate ONE UNIQUE trip option (Vibe).
    {vibe_context}
    
        DIVERSITY DIRECTIVE FOR THIS PLAN (MUST FOLLOW):
        {diversity_directive}
    
        HARD DIVERSITY CONSTRAINTS (MUST FOLLOW):
        - Define ROUTE SIGNATURE as the ordered list of STAY city names (lowercased), e.g. ["rome", "florence", "venice"].
        - Your route signature MUST NOT match ANY of these forbidden route signatures:
            {forbidden_routes_json}
        - Do NOT simply reuse the same cities in the same order with different descriptions.
        - Prefer changing at least one city and/or changing the order and number of stays.
    The option should have a unique "vibe" name (e.g., "Luxury Relax", "Adventure", "Cultural Deep Dive").
    Represent the plan as a "vibe" name and a COMPACT SEQUENCE of actions.
    
    Protocol for Actions:
    
    1. FLIGHT
       Format: ["FLIGHT", origin_city, origin_country, origin_code, dest_city, dest_country, dest_code, date, return_date, passengers, cabin]
       Note: YOU MUST PROVIDE IATA CODES. If a city does not have an airport, find and use the nearest major hub airport code.
       
    2. STAY
       Format: ["STAY", city, country, start_date, end_date, guests, rooms, description]
       Note: description is a short string of activity preferences. USE ISO-2 COUNTRY CODES (e.g., "US", "IT", "FR", "GB", "IL").
    
    CRITICAL FLIGHT RULES:
    - A trip has EXACTLY TWO FLIGHTS ONLY: one OUTBOUND flight (from origin to first destination) and one RETURN flight (from last destination back to origin).
    - NEVER add intermediate flights between destinations. Travel between cities during the trip is by ground transport (train/car), which is handled automatically - DO NOT add actions for it.
    - Example for a multi-city trip (TLV -> Rome -> Florence -> Venice -> TLV):
      * ONE outbound flight: TLV -> Rome
      * STAYS: Rome, then Florence, then Venice (consecutive)
      * ONE return flight: Venice -> TLV
      * NO flights between Rome->Florence or Florence->Venice!
    - HUB RESOLUTION: If the destination is a place without a major airport (e.g. Positano, Monaco, Gozo), you MUST use the nearest major international airport (hub) and its IATA code (e.g. NAP for Positano, NCE for Monaco, MLA for Gozo).
    - MANDATORY RETURN: Every single trip plan MUST include a return flight from the final destination back to the original starting city.
    
    Rules:
    - Generate EXACTLY ONE option.
    - Ensure logical flow: FLIGHT -> STAY(s) -> FLIGHT (exactly 2 flights total).
    - Be consistent with dates.
    - Do not include any additional text or comments.

    Creativity guidance (still must follow Trip Description):
    - GEOGRAPHIC REALISM: Only suggest multiple cities if they are geographically close enough to be easily visited within the trip duration. For example, if a trip is 5 days, don't pick cities on opposite sides of a country (e.g. don't do Berlin and Munich in 3 days) unless explicitly requested. Travel time between cities should be reasonable.
    - Choose cities that make sense geographically (contiguous travel by ground is plausible).
    - Vary the experience focus (food, history, outdoors, nightlife, wellness) in line with the "vibe".
    - If the Trip Description is underspecified, take initiative and propose a clear, distinct route.

    Trip Description:
    {trip_yml}
    
    Output JSON Example (multi-city trip with exactly 2 flights):
    {{
      "vibe": "The Classic Tourist",
      "actions": [
        ["FLIGHT", "Tel Aviv", "IL", "TLV", "Rome", "IT", "FCO", "2024-05-01", "", 2, "economy"],
        ["STAY", "Rome", "IT", "2024-05-01", "2024-05-04", 2, 1, "Colosseum and Vatican"],
        ["STAY", "Florence", "IT", "2024-05-04", "2024-05-07", 2, 1, "Renaissance art and Tuscan cuisine"],
        ["STAY", "Venice", "IT", "2024-05-07", "2024-05-10", 2, 1, "Canals and architecture"],
        ["FLIGHT", "Venice", "IT", "VCE", "Tel Aviv", "IL", "TLV", "2024-05-10", "", 2, "economy"]
      ]
    }}
    """

    response = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.1,
        top_p=0.95,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "schema": TripPlan.model_json_schema()
            }
        }
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.info(f"Failed to decode JSON from LLM: {content}")
        logger.info("DEBUG: generate_single_trip_plan returning None due to JSONDecodeError")
        return None


def generate_trip_plans_from_text(trip_yml: str, count: int = 3) -> List[Dict[str, Any]]:
    """
    Generate 3 distinct trip plans (vibes) using separate LLM calls.
    Returns a list of dicts: [{"vibe": "...", "actions": [...]}, ...]
    """
    plans: List[Dict[str, Any]] = []
    previous_vibes: List[str] = []
    forbidden_route_signatures: List[List[str]] = []
    forbidden_keys: Set[str] = set()

    diversity_directives = [
        "Classic highlights route: iconic sights, balanced pacing.",
        "Offbeat/hidden-gems route: prefer secondary cities and avoid the most standard tourist triangle.",
        "Nature/coast/wellness route: prioritize scenic towns, beaches/lakes, hiking/spas, slower travel.",
    ]

    for i in range(count):
        print(f"Generating plan {i+1}/{count}...")
        directive = diversity_directives[i % len(diversity_directives)]
        plan = generate_single_trip_plan(
            trip_yml,
            previous_vibes,
            forbidden_route_signatures,
            directive,
        )

        logger.info(f"Generating plan {i+1}/{count}...")
        if plan and "vibe" in plan:
            signature = _extract_route_signature(plan)
            sig_key = _route_signature_key(signature)
            if sig_key and sig_key in forbidden_keys:
                print(
                    f"Warning: Plan {i+1} repeated route signature: {signature}"
                )

            plans.append(plan)
            previous_vibes.append(plan["vibe"])

            if signature:
                forbidden_route_signatures.append(signature)
                forbidden_keys.add(sig_key)
        else:
            logger.info(f"Warning: Failed to generate plan {i+1}")
            
    return plans



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
       - YOU MUST PROVIDE IATA CODES. If a city does not have an airport, find and use the nearest major hub airport code (e.g. NAP for Positano).
    2. STAY: ["STAY", city, country, start_date, end_date, guests, rooms, description]
       - 'start_date' is check-in, 'end_date' is check-out. USE ISO-2 COUNTRY CODES.
    
    CRITICAL FLIGHT RULES:
    - Each trip has EXACTLY TWO FLIGHTS: one OUTBOUND (origin to first city) and one RETURN (last city back to origin). EVERY trip must have both.
    - Travel between cities during a trip is by ground transport (automatic, no action needed).
    - GEOGRAPHIC REALISM: Ensure destinations are reasonably close together for the trip's duration.
    
    Constraint & Logic Rules:
    - DATE ARITHMETIC: If a user asks to "shorten X by 1 day and give it to Y", this refers to the transition date BETWEEN X and Y.
      Example: If X is [2026-09-13 to 2026-09-17] and Y is [2026-09-17 to 2026-09-20], and the user says "shorten X by one day and give it to Y":
      * New X: [2026-09-13 to 2026-09-16]
      * New Y: [2026-09-16 to 2026-09-20]
      * The FLIGHT between X and Y must move from 2026-09-17 to 2026-09-16.
    - PHRASING: Interpret "shorten in one day" as "shorten by one day" (duration - 1).
    - CONTIGUITY: Stays and flights must remain contiguous. A check-out date for one city should generally match the check-in date for the next city and the flight date between them.
    - SPECIFICITY: Only modify the specific plan(s) mentioned (e.g., "first option"). Leave others UNCHANGED.
    - VIBE: You MAY change the "vibe" name if the user request implies a change in the overall theme, or if they explicitly ask for it.
    - VISUAL INTEGRITY: Do not modify the JSON structure unless explicitly asked.
    
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
        logger.info(f"Error parsing edited plans: {str(e)}")
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
        logger.info(f"Error: {str(e)}")
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
        logger.info(f"Error: {str(e)}")
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
        logger.info(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to edit trip plans: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)