#!/bin/bash
# Start FastAPI backend in background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend on the Cloud Run required port
streamlit run app.py \
  --server.port=8080 \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
