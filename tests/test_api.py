import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Mock google.genai to allow importing without dependency installed in tests environment
sys.modules['google.genai'] = MagicMock()
sys.modules['google.genai.types'] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app, triage_endpoint, health_check, TriageRequest
from fastapi import HTTPException

def test_health_check():
    response = health_check()
    assert response == {"status": "ok"}

@patch("main.get_secret")
@patch("main.run_extraction")
@patch("main.run_triage")
def test_triage_endpoint_success(mock_triage, mock_extraction, mock_secret):
    mock_secret.return_value = "TEST_API_KEY"
    mock_extraction.return_value = {
        "symptoms": ["chest pain"],
        "duration": "2hrs",
        "associated_signs": ["sweating"]
    }
    mock_triage.return_value = {
        "urgency_level": "RED",
        "action_plan": ["Call 911", "Provide Aspirin"]
    }

    req = TriageRequest(text="chest pain 2hrs sweating")
    data = triage_endpoint(req)
    
    assert data["status"] == "success"
    assert data["triage"]["urgency_level"] == "RED"
    assert "chest pain" in data["extracted"]["symptoms"]

@patch("main.get_secret")
def test_triage_endpoint_missing_api_key(mock_secret):
    mock_secret.return_value = ""
    req = TriageRequest(text="test")
    with patch("os.environ.get", return_value=""):
        with pytest.raises(HTTPException) as exc_info:
            triage_endpoint(req)
        assert exc_info.value.status_code == 500
