import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from agents.auth import get_secret
from agents.extractor import run_extraction
from agents.triage import run_triage

app = FastAPI(
    title="Medical Triage Bridge API",
    description="Backend mapping raw text to structured symptom and triage responses via Gemini.",
    version="0.1.0"
)

# Optional: Enable CORS for UI integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TriageRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str

@app.post("/api/triage")
def triage_endpoint(request: TriageRequest):
    # Attempt to retrieve API keys securely
    api_key = get_secret("GEMINI_API_KEY")
    # Developer override if testing locally
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GEMINI_API_KEY. Configure in Secret Manager or env.")
        
    try:
        # Agent 1: Extract medical data (Symptoms, duration)
        raw_extraction = run_extraction(request.text, api_key)
        
        # Agent 2: Triage context based on extraction
        triage_plan = run_triage(raw_extraction, api_key)
        
        return {
            "status": "success",
            "extracted": raw_extraction,
            "triage": triage_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
