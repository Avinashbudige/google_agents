import json
from pydantic import BaseModel, ConfigDict
from google import genai
from google.genai import types

class ExtractorResult(BaseModel):
    model_config = ConfigDict(extra='forbid')
    symptoms: list[str]
    duration: str
    associated_signs: list[str]

def run_extraction(text: str, api_key: str) -> dict:
    """Agent 1: Extracts structured entities from messy text."""
    client = genai.Client(api_key=api_key)
    
    config = types.GenerateContentConfig(
        system_instruction=(
            "You are a fast, precise clinical entity extractor. "
            "Extract elements from patient statements into strict JSON format with keys: "
            "symptoms (list of strings), duration (string, default to 'unknown'), "
            "and associated_signs (list of strings)."
        ),
        response_mime_type="application/json",
        response_schema=ExtractorResult,
        temperature=0.0,
        max_output_tokens=300
    )
    
    prompt = f"Extract entities from: \"{text}\""
    
    response = client.models.generate_content(
        model='gemini-1.5-pro',
        contents=prompt,
        config=config
    )
    
    return json.loads(response.text)
