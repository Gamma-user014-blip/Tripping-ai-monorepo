"""
Generate realistic vacation planning data from Pydantic models using Gemini.
Supports flight, hotel, activity, and transport models.
"""

import os
import json
import re
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


def _strip_markdown_and_clean_json(text: str) -> str:
    """
    Remove markdown code blocks and clean up the JSON response.
    
    Args:
        text: Raw text that may contain markdown code blocks
        
    Returns:
        Clean JSON string
    """
    # Remove markdown code blocks (```json ... ``` or ``` ... ```)
    text = re.sub(r'^```(?:json)?\s*\n', '', text.strip(), flags=re.MULTILINE)
    text = re.sub(r'\n```\s*$', '', text.strip(), flags=re.MULTILINE)
    
    # Remove any remaining backticks at start/end
    text = text.strip('`').strip()
    
    # Try to find JSON object/array if there's extra text
    # Look for the outermost { } or [ ]
    json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    
    return text.strip()


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
- Component scores 0.0-1.0 (preference_score: match to requested description)
- IMPORTANT: Set the "category" field to the correct integer based on activity type:
  0=UNKNOWN (use this in fallback cases), 1=TOUR, 2=MUSEUM, 3=RESTAURANT, 4=SHOW, 5=OUTDOOR, 
  6=WATER_SPORTS, 7=NIGHTLIFE, 8=SHOPPING, 9=SPA, 10=ADVENTURE, 11=CULTURAL, 12=FOOD_TOUR
  Examples: Walking tour=1, Art museum=2, Cooking class=12, Hiking=5, Snorkeling=6, Wine tasting=12
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
    You are a realistic travel data generator.
    
    {system_description or service_context}
    
    IMPORTANT INSTRUCTIONS:
    - For "options" arrays, generate exactly {list_size} diverse, realistic items
    - Use realistic names, locations, and pricing appropriate to the context
    - All scores must be between 0.0 and 1.0
    - Use ISO 8601 format for all dates and times
    - Include all required fields
    - Set "available" to true for all options
    - Generate unique IDs for each option
    """

    if preferences:
        user_prompt = f"""
Generate results for this search request:
{json.dumps(preferences, indent=2)}

Remember: Output ONLY raw JSON, no markdown formatting.
"""
    else:
        user_prompt = f"Generate {list_size} realistic travel options. Output ONLY raw JSON."

    try:
        if provider == LLMProvider.PERPLEXITY:
            raw_text = _generate_with_perplexity(system_prompt, user_prompt, response_model=schema)
        else:
            raw_text = _generate_with_gemini(system_prompt, user_prompt, use_grounding)

        # Strip markdown and clean the response
        cleaned_text = _strip_markdown_and_clean_json(raw_text)
        
        return json.loads(cleaned_text)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse {provider} response as JSON: {e}\n"
            f"Raw response:\n{raw_text}\n"
            f"Cleaned response:\n{cleaned_text if 'cleaned_text' in locals() else 'N/A'}"
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