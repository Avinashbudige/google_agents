import sys
import os
import time
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

# Mock google.genai before importing modules that depend on it
sys.modules['google.genai'] = MagicMock()
sys.modules['google.genai.types'] = MagicMock()
sys.modules['google.oauth2'] = MagicMock()
sys.modules['google.oauth2.service_account'] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import triage_endpoint, health_check, TriageRequest
from fastapi import HTTPException

# ─────────────────────────────────────────────
# SHARED FIXTURE
# ─────────────────────────────────────────────
@pytest.fixture
def mock_agents():
    """Mocks both Vertex AI agents (extractor + triage)."""
    with patch("main.run_extraction") as mock_extract, \
         patch("main.run_triage") as mock_triage:
        yield mock_extract, mock_triage


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
def test_health():
    assert health_check() == {"status": "ok"}


# ─────────────────────────────────────────────
# USE CASE 1: Classic cardiac emergency → RED
# ─────────────────────────────────────────────
def test_chest_pain_sweating_red(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": ["chest pain"], "duration": "2hrs",
        "associated_signs": ["sweating", "left arm pain"]
    }
    mock_triage.return_value = {
        "urgency_level": "RED",
        "action_plan": ["Call 108 ambulance immediately", "Chew aspirin 325mg", "Do not eat or drink"]
    }
    start = time.time()
    res = triage_endpoint(TriageRequest(text="chest pain 2hrs sweating left arm pain"))
    assert time.time() - start < 1.2, "Latency exceeded 1.2s"
    assert res["triage"]["urgency_level"] == "RED"
    assert any("108" in step for step in res["triage"]["action_plan"])


# ─────────────────────────────────────────────
# USE CASE 2: Breathing difficulty → RED
# ─────────────────────────────────────────────
def test_breathing_difficulty_red(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": ["difficulty breathing"], "duration": "30min",
        "associated_signs": ["wheezing", "blue lips"]
    }
    mock_triage.return_value = {
        "urgency_level": "RED",
        "action_plan": ["Call emergency services", "Sit upright", "Use inhaler if available"]
    }
    res = triage_endpoint(TriageRequest(text="can't breathe properly wheezing blue lips 30 mins"))
    assert res["triage"]["urgency_level"] == "RED"
    assert any("emergency" in s.lower() for s in res["triage"]["action_plan"])


# ─────────────────────────────────────────────
# USE CASE 3: Stroke symptoms → RED
# ─────────────────────────────────────────────
def test_stroke_symptoms_red(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": ["facial drooping", "slurred speech"], "duration": "1hr",
        "associated_signs": ["arm weakness", "sudden confusion"]
    }
    mock_triage.return_value = {
        "urgency_level": "RED",
        "action_plan": ["Call 108 immediately", "Note exact time symptoms started", "Do not give food or water"]
    }
    res = triage_endpoint(TriageRequest(text="face drooping slurred speech arm weak confused 1hr ago"))
    assert res["triage"]["urgency_level"] == "RED"
    assert res["extracted"]["symptoms"] == ["facial drooping", "slurred speech"]


# ─────────────────────────────────────────────
# USE CASE 4: High fever with seizure risk → YELLOW
# ─────────────────────────────────────────────
def test_high_fever_yellow(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": ["high fever"], "duration": "2 days",
        "associated_signs": ["temperature 104F", "shivering"]
    }
    mock_triage.return_value = {
        "urgency_level": "YELLOW",
        "action_plan": ["Visit ER within 2 hours", "Take paracetamol 500mg", "Cool compresses on forehead"]
    }
    res = triage_endpoint(TriageRequest(text="fever 104F shivering last 2 days"))
    assert res["triage"]["urgency_level"] == "YELLOW"
    assert res["status"] == "success"


# ─────────────────────────────────────────────
# USE CASE 5: Abdominal pain + vomiting → YELLOW
# ─────────────────────────────────────────────
def test_abdominal_pain_vomiting_yellow(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": ["abdominal pain", "vomiting"], "duration": "6hrs",
        "associated_signs": ["nausea", "no fever"]
    }
    mock_triage.return_value = {
        "urgency_level": "YELLOW",
        "action_plan": ["See doctor within 4hrs", "Stay hydrated with sips of water", "Avoid solid food temporarily"]
    }
    res = triage_endpoint(TriageRequest(text="stomach pain vomiting last 6 hours nausea no fever"))
    assert res["triage"]["urgency_level"] == "YELLOW"
    assert len(res["triage"]["action_plan"]) >= 2


# ─────────────────────────────────────────────
# USE CASE 6: Mild headache → GREEN
# ─────────────────────────────────────────────
def test_mild_headache_green(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": ["headache"], "duration": "2hrs",
        "associated_signs": []
    }
    mock_triage.return_value = {
        "urgency_level": "GREEN",
        "action_plan": ["Rest in a quiet dark room", "Take paracetamol", "Stay hydrated"]
    }
    res = triage_endpoint(TriageRequest(text="headache for 2 hours"))
    assert res["triage"]["urgency_level"] == "GREEN"
    assert any("paracetamol" in s.lower() for s in res["triage"]["action_plan"])


# ─────────────────────────────────────────────
# USE CASE 7: Mild fever → GREEN
# ─────────────────────────────────────────────
def test_mild_fever_green(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": ["mild fever"], "duration": "1 day",
        "associated_signs": ["runny nose", "sore throat"]
    }
    mock_triage.return_value = {
        "urgency_level": "GREEN",
        "action_plan": ["Monitor 24hrs", "Rest at home", "Paracetamol if temp rises above 38.5°C"]
    }
    res = triage_endpoint(TriageRequest(text="mild fever runny nose sore throat yesterday"))
    assert res["triage"]["urgency_level"] == "GREEN"
    assert "Monitor 24hrs" in res["triage"]["action_plan"]


# ─────────────────────────────────────────────
# USE CASE 8: Minor cut / skin wound → GREEN
# ─────────────────────────────────────────────
def test_minor_cut_green(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": ["small cut on finger"], "duration": "just now",
        "associated_signs": ["bleeding stopped"]
    }
    mock_triage.return_value = {
        "urgency_level": "GREEN",
        "action_plan": ["Clean wound with water", "Apply antiseptic", "Cover with bandage"]
    }
    res = triage_endpoint(TriageRequest(text="small cut on my finger bleeding stopped"))
    assert res["triage"]["urgency_level"] == "GREEN"
    assert res["extracted"]["duration"] == "just now"


# ─────────────────────────────────────────────
# USE CASE 9: Edge case — gibberish input
# ─────────────────────────────────────────────
def test_gibberish_unable_to_assess(mock_agents):
    mock_extract, mock_triage = mock_agents
    mock_extract.return_value = {
        "symptoms": [], "duration": "unknown",
        "associated_signs": []
    }
    mock_triage.return_value = {
        "urgency_level": "YELLOW",
        "action_plan": ["Unable to assess — please describe symptoms clearly", "Consult a physician"]
    }
    res = triage_endpoint(TriageRequest(text="asdfghjkl qwerty 123"))
    assert "Unable to assess" in res["triage"]["action_plan"][0]


# ─────────────────────────────────────────────
# USE CASE 10: Security — empty string input
# ─────────────────────────────────────────────
def test_empty_input_rejected():
    with pytest.raises(ValidationError):
        TriageRequest(text="")


# ─────────────────────────────────────────────
# SECURITY: Oversized payload (>1000 chars)
# ─────────────────────────────────────────────
def test_oversized_payload_rejected():
    with pytest.raises(ValidationError):
        TriageRequest(text="a" * 1001)
