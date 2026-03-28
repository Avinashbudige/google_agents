import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("main.get_secret")
@patch("main.run_extraction")
@patch("main.run_triage")
def test_triage_endpoint_success(mock_triage, mock_extraction, mock_secret):
    # Mocking external calls
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

    response = client.post(
        "/api/triage",
        json={"text": "chest pain 2hrs sweating"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["triage"]["urgency_level"] == "RED"
    assert "chest pain" in data["extracted"]["symptoms"]

def test_triage_endpoint_missing_body():
    # FastAPI automatically handles missing fields with 422 Unprocessable Entity
    response = client.post("/api/triage", json={})
    assert response.status_code == 422

@patch("main.get_secret")
def test_triage_endpoint_missing_api_key(mock_secret):
    # Setup missing key flow via monkeypatch or directly mocking environmental fallbacks
    mock_secret.return_value = ""
    with patch("os.environ.get", return_value=""):
        response = client.post("/api/triage", json={"text": "test"})
        # The backend throws a 500 when keys are completely missing
        assert response.status_code == 500
