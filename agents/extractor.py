import os
import re
import json
from google import genai
from google.genai import types
from google.oauth2 import service_account

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "aiagents-491012")
LOCATION   = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
SA_KEY_FILE = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    r"D:\nishkama karma\nidhidyasana\reverse_engineering\google_agents\aiagents-491012-c053d887095c.json"
)

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def _get_credentials():
    return service_account.Credentials.from_service_account_file(
        SA_KEY_FILE, scopes=SCOPES
    )

def _parse_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON cleanly."""
    # Remove ```json ... ``` or ``` ... ``` fences
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    # Find the first JSON object in the text
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(raw)

def run_extraction(text: str, api_key: str = "") -> dict:
    """Agent 1: Extracts structured entities from messy text via Vertex AI ADC."""
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        credentials=_get_credentials(),
    )

    config = types.GenerateContentConfig(
        system_instruction=(
            "You are a fast, precise clinical entity extractor. "
            "You MUST reply with ONLY a valid JSON object — no markdown, no explanation. "
            "JSON keys: symptoms (list of strings), duration (string, default 'unknown'), "
            "associated_signs (list of strings)."
        ),
        response_mime_type="application/json",
        temperature=0.0,
        max_output_tokens=300
    )

    prompt = f'Extract entities from: "{text}"'

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )

    raw = response.text if response.text else ""
    if not raw and response.candidates:
        raw = response.candidates[0].content.parts[0].text
    print(f"[EXTRACTOR RAW]: {repr(raw)}")
    return _parse_json(raw)
