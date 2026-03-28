import json
from pydantic import BaseModel, ConfigDict
from google import genai
from google.genai import types

class TriageResult(BaseModel):
    model_config = ConfigDict(extra='forbid')
    urgency_level: str
    action_plan: list[str]

def run_triage(extracted_data: dict, api_key: str) -> dict:
    """Agent 2: Triages patient data into actionable urgency levels."""
    client = genai.Client(api_key=api_key)
    
    config = types.GenerateContentConfig(
        system_instruction=(
            "You are an expert clinical triage agent. Read the provided extracted components and determine urgency. "
            "You MUST output exactly one urgency_level ('RED', 'YELLOW', or 'GREEN'). "
            "RED = life-threatening or severe "
            "YELLOW = urgent but stable "
            "GREEN = non-urgent routine care. "
            "And provide a concise bullet action_plan (list of strings)."
        ),
        response_mime_type="application/json",
        response_schema=TriageResult,
        temperature=0.1,
        max_output_tokens=300
    )
    
    prompt = f"Triage the following details:\n{json.dumps(extracted_data)}"
    
    response = client.models.generate_content(
        model='gemini-1.5-pro',
        contents=prompt,
        config=config
    )
    
    return json.loads(response.text)
