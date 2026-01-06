"""
Generate realistic vacation planning data from Pydantic models using Gemini.
Supports flight, hotel, activity, and transport models.
"""

import os
import json
from google import genai
from dotenv import load_dotenv

from apps.data_collectors.llm_retreiver.llm_provider import LLMProvider
from apps.data_collectors.llm_retreiver.gemini_generator import _generate_with_gemini
from apps.data_collectors.llm_retreiver.perplexity_generator import _generate_with_perplexity

# Import Pydantic models
from shared.data_types import models

load_dotenv()
TOKEN = os.getenv("GEMINI_API_TOKEN") or os.getenv("GEMINI_API_KEY")
if not TOKEN:
    raise ValueError("Set GEMINI_API_TOKEN or GEMINI_API_KEY environment variable")

CLIENT = genai.Client(api_key=TOKEN)


def _get_service_context(model_name: str) -> str:
    """Get context-specific instructions for each service type."""
    
    contexts = {
        "FlightSearchResponse": """
Generate realistic flight options with:
- Real airline names (United, Delta, American, British Airways, etc.)
- Realistic routes and IATA airport codes
- Appropriate pricing: economy $200-800, business $1000-3000, first $1500-5000
- Realistic flight durations based on distance
- 0-2 stops for most routes
- ISO 8601 datetime format (YYYY-MM-DDTHH:MM:SS)
- Include layover details when stops > 0
- Amenities appropriate to cabin class
- Component scores 0.0-1.0 (price_score: lower price = higher, quality_score: better service/fewer stops)
""",
        "ActivitySearchResponse": """
Generate realistic activity options with:
- Location-appropriate activities (tours, museums, outdoor activities, food tours)
- Pricing $10-300 depending on activity type
- Ratings 3.5-5.0
- Duration 60-480 minutes (1-8 hours)
- Realistic highlights and inclusions
- Available time slots with ISO 8601 format (date: YYYY-MM-DD, time: HH:MM)
- Difficulty levels: easy, moderate, challenging
- Component scores 0.0-1.0 (preference_score: match to requested categories)
""",
        "TransportSearchResponse": """
Generate realistic transport options with:
- Appropriate modes for distance (rental car, rideshare, train, bus)
- Realistic providers (Hertz, Uber, Amtrak, Greyhound, etc.)
- Distance-appropriate pricing and duration
- Vehicle details: class, model, seats, features
- ISO 8601 datetime format (YYYY-MM-DDTHH:MM:SS)
- For rental cars: economy, compact, SUV classes with daily rates
- For rideshare: sedan, SUV, van options with wait times
- For transit: line numbers, stops, service class
- Component scores 0.0-1.0 (convenience_score: shorter duration/wait = higher)
""",
    }
    
    return contexts.get(model_name, "Generate realistic travel-related data.")


def generate_json_from_model(
    model_cls,
    list_size: int = 1,
    preferences: dict = None,
    system_description: str = None,
    use_grounding: bool = False,
    provider: LLMProvider = LLMProvider.PERPLEXITY,
):
    schema = model_cls.model_json_schema()
    model_name = model_cls.__name__

    service_context = _get_service_context(model_name)

    system_prompt = f"""
OUTPUT ONLY RAW JSON. DO NOT USE MARKDOWN OR CODE BLOCKS.

{system_description or service_context}

The JSON MUST strictly follow this schema:
{json.dumps(schema, indent=2)}

IMPORTANT INSTRUCTIONS:
- For "options" arrays, generate exactly {list_size} diverse, realistic items
- Use realistic names, locations, and pricing appropriate to the context
- All scores must be between 0.0 and 1.0
- Use ISO 8601 format for all dates and times
- Include all required fields from the schema
- Set "available" to true for all options
- Generate unique IDs for each option
"""

    if preferences:
        user_prompt = f"""
Generate results for this search request:
{json.dumps(preferences, indent=2)}
"""
    else:
        user_prompt = f"Generate {list_size} realistic travel options."

    try:
        if provider == LLMProvider.PERPLEXITY:
            raw_text = _generate_with_perplexity(system_prompt, user_prompt)
        else:
            raw_text = _generate_with_gemini(system_prompt, user_prompt, use_grounding)

        return json.loads(raw_text)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse {provider} response as JSON: {e}\nResponse:\n{raw_text}"
        )


def generate_model_message(model_cls, request_dict: dict = None, list_size: int = 5):
    """
    Generate a populated Pydantic model using Gemini.
    
    Args:
        model_cls: Pydantic response class (e.g., models.FlightSearchResponse)
        request_dict: Optional request parameters as dict
        list_size: Number of options to generate
    
    Returns:
        Populated Pydantic model
    """
    json_data = generate_json_from_model(
        model_cls=model_cls,
        list_size=list_size,
        preferences=request_dict
    )
    
    # Convert JSON to Pydantic model
    message = model_cls.model_validate(json_data)
    
    return message
