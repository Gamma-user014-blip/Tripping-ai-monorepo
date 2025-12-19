import os
import json
from google import genai
from google.genai import types
from google.protobuf.descriptor import FieldDescriptor
from dotenv import load_dotenv
import data_types.types_pb2 as data_types

load_dotenv()
TOKEN = os.getenv("GEMINI_API_TOKEN")
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
        else:
            field_schema["type"] = TYPE_MAP.get(field.type, "string")

        if field.label == FieldDescriptor.LABEL_REPEATED:
            field_schema = {"type": "array", "items": field_schema}
        else:
            schema["required"].append(field.name)

        schema["properties"][field.name] = field_schema

    return schema


def generate_json_from_proto(
    proto_cls,
    list_size: int = 1,
    preferences: dict = None,
    system_description: str = "if you see this dont generate"
):
    """
    Generate JSON content using Gemini for a given protobuf class.
    
    Args:
        proto_cls: Protobuf class to generate schema from.
        list_size: Number of items in repeated fields (if applicable).
        preferences: Optional dict of preferences to influence content.
        system_description: Optional system prompt description.
    
    Returns:
        JSON dict following the protobuf schema.
    """
    schema = _proto_to_json_schema(proto_cls)


    system_prompt = f"""
    NO MARKDOWN, RAW TEXT ONLY.
        {system_description}
        The JSON MUST strictly follow this schema:
        {json.dumps(schema, indent=2)}

        For repeated fields, generate exactly {list_size} items.
        """

    grounding_tool = types.Tool(google_search=types.GoogleSearch())

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[grounding_tool]
)

    response = CLIENT.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=preferences or "",
        config=config,
    )

    # Gemini response might be string, parse to dict
    try:
        return json.loads(response.text)
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {e}")