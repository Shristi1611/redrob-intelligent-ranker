import streamlit as st
import json
from shared_ui import inject_global_styles, render_sidebar_footer

inject_global_styles()
render_sidebar_footer()

st.markdown('<p class="section-heading">Step 01</p>', unsafe_allow_html=True)
st.markdown('<p class="section-title">Load candidates</p>', unsafe_allow_html=True)

source = st.radio(
    "Data source",
    ["Bundled sample, 50 candidates", "Upload your own JSON / JSONL"],
    horizontal=True,
    label_visibility="collapsed",
)

candidates = None

if source.startswith("Bundled"):
    try:
        with open("sample_candidates.json") as f:
            candidates = json.load(f)
        st.success(f"Loaded {len(candidates)} candidates from sample_candidates.json")
    except FileNotFoundError:
        st.error("sample_candidates.json not found in this deployment.")
else:
    uploaded = st.file_uploader("Upload file", type=["json", "jsonl"], label_visibility="collapsed")
    if uploaded is not None:
        content = uploaded.read().decode("utf-8")
        try:
            if uploaded.name.endswith(".jsonl"):
                candidates = [json.loads(line) for line in content.splitlines() if line.strip()]
            else:
                candidates = json.loads(content)
            st.success(f"Loaded {len(candidates)} candidates from {uploaded.name}")
        except Exception as e:
            st.error(f"Could not parse file: {e}")

if candidates:
    st.session_state["candidates"] = candidates
    st.write("")
    st.info("Candidates are loaded. Go to the Results page in the sidebar to run the ranker.")
else:
    st.write("")
    st.info("Choose a data source above to load candidates.")