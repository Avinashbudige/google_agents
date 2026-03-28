import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
    text: str = Field(..., min_length=1, max_length=1000)

@app.post("/api/triage")
def triage_endpoint(request: TriageRequest):
    try:
        # Agent 1: Extract medical data (Symptoms, duration)
        raw_extraction = run_extraction(request.text)

        # Agent 2: Triage context based on extraction
        triage_plan = run_triage(raw_extraction)

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
