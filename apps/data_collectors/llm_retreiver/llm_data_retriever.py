"""
Generate realistic vacation planning data from protobuf schemas using Gemini.
Supports flight, hotel, activity, and transport proto files.
"""

import os
import json
from google import genai
from google.genai import types
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.json_format import ParseDict
from dotenv import load_dotenv

from apps.data_collectors.llm_retreiver.llm_provider import LLMProvider
from apps.data_collectors.llm_retreiver.gemini_generator import _generate_with_gemini
from apps.data_collectors.llm_retreiver.perplexity_generator import _generate_with_perplexity

# Import your proto files
try:
    import shared.data_types.common_pb2 as common_pb2
    import shared.data_types.flight_pb2 as flight_pb2
    import shared.data_types.hotel_pb2 as hotel_pb2
    import shared.data_types.activity_pb2 as activity_pb2   
    import shared.data_types.transport_pb2 as transport_pb2
except ImportError:
    print("Warning: Proto files not found. Generate them with: protoc --python_out=. *.proto")

load_dotenv()
TOKEN = os.getenv("GEMINI_API_TOKEN") or os.getenv("GEMINI_API_KEY")
if not TOKEN:
    raise ValueError("Set GEMINI_API_TOKEN or GEMINI_API_KEY environment variable")

CLIENT = genai.Client(api_key=TOKEN)


def _proto_to_json_schema(message_cls):
    """
    Convert a protobuf message class to a JSON Schema dict.
    """
    descriptor = message_cls.DESCRIPTOR

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": descriptor.name,
        "type": "object",
        "properties": {},
        "required": []
    }

    TYPE_MAP = {
        FieldDescriptor.TYPE_STRING: "string",
        FieldDescriptor.TYPE_INT32: "integer",
        FieldDescriptor.TYPE_INT64: "integer",
        FieldDescriptor.TYPE_FLOAT: "number",
        FieldDescriptor.TYPE_DOUBLE: "number",
        FieldDescriptor.TYPE_BOOL: "boolean",
        FieldDescriptor.TYPE_ENUM: "string",
        FieldDescriptor.TYPE_MESSAGE: "object",
    }

    for field in descriptor.fields:
        field_schema = {}

        if field.type == FieldDescriptor.TYPE_MESSAGE:
            # Nested message
            field_schema = _proto_to_json_schema(field.message_type._concrete_class)
        elif field.type == FieldDescriptor.TYPE_ENUM:
            # Enum - list valid values
            enum_values = [v.name for v in field.enum_type.values]
            field_schema = {
                "type": "string",
                "enum": enum_values,
                "description": f"Enum values: {', '.join(enum_values)}"
            }
        else:
            field_schema["type"] = TYPE_MAP.get(field.type, "string")

        if field.label == FieldDescriptor.LABEL_REPEATED:
            field_schema = {"type": "array", "items": field_schema}
        else:
            schema["required"].append(field.name)

        schema["properties"][field.name] = field_schema

    return schema


def _get_service_context(proto_cls_name: str) -> str:
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
        "HotelSearchResponse": """
Generate realistic hotel options with:
- Real hotel chains (Marriott, Hilton, Hyatt, InterContinental, etc.)
- Appropriate pricing per night: budget $50-100, midscale $100-250, upscale $250-500, luxury $500+
- Ratings 3.0-5.0 (correlate with price/category)
- Star ratings 1-5
- Distance to city center: 0.5-5km
- Realistic amenities for category (wifi, pool, gym, spa, etc.)
- Room types: standard, deluxe, suite
- ISO 8601 date format (YYYY-MM-DD)
- Component scores 0.0-1.0 (price_score: lower price = higher, quality_score: rating/amenities)
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
    
    return contexts.get(proto_cls_name, "Generate realistic travel-related data.")


def generate_json_from_proto(
    proto_cls,
    list_size: int = 1,
    preferences: dict = None,
    system_description: str = None,
    use_grounding: bool = False,
    provider: LLMProvider = LLMProvider.PERPLEXITY,
):
    schema = _proto_to_json_schema(proto_cls)
    proto_name = proto_cls.DESCRIPTOR.name

    service_context = _get_service_context(proto_name)

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


def generate_proto_message(proto_cls, request_dict: dict = None, list_size: int = 5):
    """
    Generate a populated protobuf message using Gemini.
    
    Args:
        proto_cls: Protobuf response class (e.g., flight_pb2.FlightSearchResponse)
        request_dict: Optional request parameters as dict
        list_size: Number of options to generate
    
    Returns:
        Populated protobuf message
    """
    json_data = generate_json_from_proto(
        proto_cls=proto_cls,
        list_size=list_size,
        preferences=request_dict
    )
    
    # Convert JSON to protobuf message
    message = proto_cls()
    ParseDict(json_data, message, ignore_unknown_fields=True)
    
    return message