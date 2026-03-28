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
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(raw)

def run_triage(extracted_data: dict, api_key: str = "") -> dict:
    """Agent 2: Triages patient data into actionable urgency levels via Vertex AI ADC."""
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        credentials=_get_credentials(),
    )

    config = types.GenerateContentConfig(
        system_instruction=(
            "You are an expert clinical triage agent. "
            "You MUST reply with ONLY a valid JSON object — no markdown, no explanation. "
            "JSON keys: urgency_level (string: RED, YELLOW, or GREEN), "
            "action_plan (list of strings). "
            "RED = life-threatening. YELLOW = urgent but stable. GREEN = routine care."
        ),
        response_mime_type="application/json",
        temperature=0.1,
        max_output_tokens=800
    )

    prompt = f"Triage the following patient details:\n{json.dumps(extracted_data)}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )

    raw = response.text if response.text else ""
    if not raw and response.candidates:
        raw = response.candidates[0].content.parts[0].text
    print(f"[TRIAGE RAW]: {repr(raw)}")
    return _parse_json(raw)
