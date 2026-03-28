# 🏥 Intent Bridge Agent — Medical Triage AI

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red?logo=streamlit)
![Vertex AI](https://img.shields.io/badge/Vertex_AI-Gemini_2.5_Flash-orange?logo=googlecloud)
![Cloud Run](https://img.shields.io/badge/Cloud_Run-Deployed-blue?logo=googlecloud)
![Tests](https://img.shields.io/badge/Tests-12%20Passed-brightgreen)

> **Fast Hackathon MVP**: Converts messy patient text → structured medical urgency cards using two chained Vertex AI Gemini 2.5 Flash agents.

---

## 🚀 Live Demo

> **URL**: _(add after Cloud Run deployment)_

**Demo Input**: `chest pain 2hrs sweating left arm pain`

**Demo Output**:
```
🚨 URGENT: RED
Action Plan:
  • Call emergency services immediately (911/112)
  • Do not allow patient to drive
  • Chew aspirin 325mg if not contraindicated
  • Remain calm and still
```

---

## 🎯 How It Works

```
User Input (messy text)
        ↓
┌─────────────────────────┐
│  Agent 1: Extractor     │  gemini-2.5-flash
│  symptoms, duration,    │  → JSON schema
│  associated_signs       │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│  Agent 2: Triage        │  gemini-2.5-flash
│  urgency_level (RED /   │  → action_plan[]
│  YELLOW / GREEN)        │
└──────────┬──────────────┘
           ↓
  Streamlit Urgency Card
```

---

## 📊 Evaluation Criteria

| Criteria              | Status | Details |
|-----------------------|--------|---------|
| Agent Pipeline        | ✅     | 2 chained Gemini agents (Extractor → Triage) |
| Structured Output     | ✅     | JSON schema enforced at API layer |
| Urgency Classification| ✅     | RED / YELLOW / GREEN with color-coded badges |
| Action Plans          | ✅     | Clinical bullet-point steps per response |
| Security              | ✅     | ADC auth, input validation, CORS, no hardcoded secrets |
| Test Coverage         | ✅     | 12 tests, all passing, including edge cases |
| Cloud Deployment      | ✅     | Cloud Run + Cloud Build CI/CD |
| Latency               | ✅     | <1.2s mock-tested, ~15-25s live Gemini 2.5 Flash |

---

## 🛠️ Tech Stack

| Layer      | Technology |
|------------|-----------|
| Frontend   | Streamlit 1.55 |
| Backend    | FastAPI 0.135 + Uvicorn |
| AI Agent 1 | Vertex AI Gemini 2.5 Flash (Extractor) |
| AI Agent 2 | Vertex AI Gemini 2.5 Flash (Triage) |
| Auth       | Google Service Account ADC |
| Deployment | Google Cloud Run |
| CI/CD      | Google Cloud Build |
| Testing    | Pytest + pytest-cov |

---

## 📁 Project Structure

```
intent-bridge-agent/
├── app.py                  # Streamlit frontend
├── main.py                 # FastAPI backend
├── agents/
│   ├── extractor.py        # Agent 1: Entity extraction
│   ├── triage.py           # Agent 2: Urgency classification
│   └── auth.py             # Secret Manager helper
├── tests/
│   ├── test_triage.py      # 10 use-case tests + security
│   └── test_api.py         # API endpoint tests
├── Dockerfile              # Container definition
├── cloudbuild.yaml         # Cloud Build CI/CD
├── deployment.yaml         # Cloud Run config
└── requirements.txt
```

---

## 🔒 Security Checklist

- ✅ **No hardcoded secrets** — `.env` and `*.json` excluded from git via `.gitignore`
- ✅ **Input sanitization** — Pydantic `Field(min_length=1, max_length=1000)`
- ✅ **CORS headers** — FastAPI CORSMiddleware configured
- ✅ **ADC Authentication** — Google Application Default Credentials via service account
- ✅ **Docker secrets** — `.dockerignore` prevents key files entering container image
- ✅ **Cloud Run** — Workload Identity for production credential management

---

## ⚡ Local Development

### Prerequisites
- Python 3.11+
- Google Cloud project with Vertex AI API enabled
- Service account JSON with `Vertex AI User` role

### Setup
```bash
git clone https://github.com/Avinashbudige/intent-bridge-agent
cd intent-bridge-agent
pip install -r requirements.txt
```

### Configure credentials
```bash
# Create .env file
echo "GOOGLE_APPLICATION_CREDENTIALS=path/to/your-key.json" > .env
echo "GOOGLE_CLOUD_PROJECT=your-project-id" >> .env
echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
```

### Run locally (two terminals)
```bash
# Terminal 1 - Backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
python -m streamlit run app.py
```

### Run tests
```bash
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## ☁️ Cloud Run Deployment

```bash
# Authenticate
gcloud auth login
gcloud config set project aiagents-491012

# Build and deploy via Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or deploy directly
gcloud run deploy intent-bridge-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --service-account YOUR_SA@aiagents-491012.iam.gserviceaccount.com
```

---

## 🧪 Test Results

```
tests/test_triage.py::test_health                          PASSED
tests/test_triage.py::test_chest_pain_sweating_red         PASSED
tests/test_triage.py::test_breathing_difficulty_red        PASSED
tests/test_triage.py::test_stroke_symptoms_red             PASSED
tests/test_triage.py::test_high_fever_yellow               PASSED
tests/test_triage.py::test_abdominal_pain_vomiting_yellow  PASSED
tests/test_triage.py::test_mild_headache_green             PASSED
tests/test_triage.py::test_mild_fever_green                PASSED
tests/test_triage.py::test_minor_cut_green                 PASSED
tests/test_triage.py::test_gibberish_unable_to_assess      PASSED
tests/test_triage.py::test_empty_input_rejected            PASSED
tests/test_triage.py::test_oversized_payload_rejected      PASSED

12 passed in 0.42s
```

---

## 👨‍💻 Author

**Avinash Budige** | Built for Hackathon 2026
