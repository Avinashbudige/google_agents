"""Quick script to list available Gemini models in your Vertex AI project."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google import genai
from google.oauth2 import service_account

SA_KEY = r"D:\nishkama karma\nidhidyasana\reverse_engineering\google_agents\aiagents-491012-c053d887095c.json"
PROJECT = "aiagents-491012"
LOCATION = "us-central1"

creds = service_account.Credentials.from_service_account_file(
    SA_KEY, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION, credentials=creds)

print("Available models:")
for m in client.models.list():
    if "gemini" in m.name.lower():
        print(" -", m.name)
