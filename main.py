import os
import logging
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secure CORS: Default to local Streamlit ports unless overridden
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:8501,http://localhost:8080").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class TriageRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str = Field(..., min_length=1, max_length=1000)

@app.post("/api/triage")
async def triage_endpoint(request: TriageRequest):
    try:
        # Agent 1: Extract medical data (Symptoms, duration) - NOW ASYNC
        raw_extraction = await run_extraction(request.text)

        # Agent 2: Triage context based on extraction - NOW ASYNC
        triage_plan = await run_triage(raw_extraction)

        return {
            "status": "success",
            "extracted": raw_extraction,
            "triage": triage_plan
        }
    except Exception as e:
        # Log the detailed exception securely to internal console/logs
        logger.error(f"Internal API Error during triage: {repr(e)}", exc_info=True)
        # Prevent stack/detail leakage to frontend 
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing the triage request.")

@app.get("/health")
def health_check():
    return {"status": "ok"}
