import streamlit as st
import httpx
import os

# Ensure fast loading, a11y via markdown and alt labels natively
st.set_page_config(page_title="Medical Triage Bridge Agent", page_icon="🏥", layout="centered")

st.title("🏥 Medical Triage Bridge Agent")
st.markdown("Fast Hackathon MVP: **Triages chaotic statements via Gemini 1.5 Pro Agents into visual action plans.**")

# A11y input section
user_input = st.text_area(
    "Patient Messy Input:",
    height=100,
    placeholder="E.g., chest pain 2hrs sweating",
    help="Enter symptoms as reported by the patient."
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/triage")
# Ensure httpx timeout isn't too strict, but short enough to demonstrate latency requirements
TIMEOUT_SEC = 10.0

if st.button("Evaluate Triage", type="primary", use_container_width=True):
    if user_input.strip() == "":
        st.error("Please enter patient symptoms to process.")
    else:
        with st.spinner("Processing via Vertex AI Pipeline (Extractor -> Triage)..."):
            try:
                response = httpx.post(API_URL, json={"text": user_input}, timeout=TIMEOUT_SEC)
                
                if response.status_code == 200:
                    data = response.json()
                    triage_info = data.get("triage", {})
                    extracted_info = data.get("extracted", {})
                    
                    urgency = triage_info.get("urgency_level", "GREEN")
                    action_plan = triage_info.get("action_plan", [])
                    
                    # Layout UI visually using distinct accessible contrast cues
                    st.divider()
                    
                    # Generate Badge dynamically
                    if urgency == "RED":
                        st.error(f"## 🚨 URGENT: {urgency}")
                    elif urgency == "YELLOW":
                        st.warning(f"## ⚠️ PRIORITY: {urgency}")
                    else:
                        st.success(f"## ✅ ROUTINE: {urgency}")
                        
                    # Build Cards Layout
                    col1, col2 = st.columns([1.5, 1])
                    with col1:
                        st.subheader("📋 Action Plan")
                        for step in action_plan:
                            st.markdown(f"- {step}")
                            
                    with col2:
                        st.subheader("🔍 Extraction Base")
                        st.json(extracted_info)
                        
                else:
                    st.error(f"Backend API Error: {response.text}")
            except Exception as e:
                st.error(f"Network Connection Failed: Verify Backend is running. ({str(e)})")
