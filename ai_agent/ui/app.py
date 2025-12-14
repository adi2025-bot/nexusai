import streamlit as st
import requests
import uuid
import time
import sys
import os

# Add root directory to sys.path to allow imports from ai_agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai_agent.services.output_formatter import OutputFormatter
from ai_agent.core.schemas import Source, ReasoningStep

st.set_page_config(page_title="Atlas AI Agent", page_icon="🤖", layout="wide")
API_URL = "http://localhost:8000"

# --- Styles ---
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Header ---
st.title("🤖 Atlas")
st.caption("Autonomous Research & Task Assistant powered by Groq")

# --- Sidebar ---
with st.sidebar:
    st.header("Control Panel")
    if st.button("New Session", type="primary", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    st.caption(f"Session: `{st.session_state.session_id[:8]}`")
    
    # Status Check
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("● System Operational")
        else:
            st.error("● System Issues")
    except:
        st.error("● API Offline")

# --- Interface ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Enter your research topic or task..."):
    # User message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Agent Response
    with st.chat_message("assistant"):
        with st.spinner("Atlas is researching..."):
            try:
                payload = {
                    "query": prompt,
                    "session_id": st.session_state.session_id,
                    "output_format": "markdown"
                }
                
                # Call Backend
                response = requests.post(f"{API_URL}/chat", json=payload, timeout=120)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Reconstruct objects from JSON response
                    sources = [Source(**s) for s in data.get('sources', [])]
                    chain = [ReasoningStep(**s) for s in data.get('reasoning_chain', [])]
                    
                    # Format
                    formatted_response = OutputFormatter.format_as_markdown(
                        data['response_text'],
                        sources,
                        chain
                    )
                    
                    st.markdown(formatted_response, unsafe_allow_html=True)
                    st.caption(f"⏱️ {data['execution_time_sec']:.2f}s execution time")
                    
                    st.session_state.messages.append({"role": "assistant", "content": formatted_response})
                else:
                    st.error(f"API Error: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: Is the backend running? ({e})")
