import streamlit as st
import json
import pandas as pd
import time

from ranker import (
    rank_candidates,
    is_honeypot,
    score_career,
    score_skills,
    score_behavioral,
    score_experience,
    score_profile,
)

st.set_page_config(page_title="Redrob Intelligent Ranker — Sandbox", layout="wide")

st.title("Redrob Intelligent Ranker")
st.caption(
    "Career-history-first candidate ranking. Skills only count when career "
    "history demonstrates real use — keyword stuffing gets discounted."
)

st.divider()

# ----------------------------------------------------------------
# Data source selection
# ----------------------------------------------------------------
st.subheader("1. Load candidates")

source = st.radio(
    "Choose a data source",
    ["Use bundled sample_candidates.json (50 candidates)", "Upload your own JSON/JSONL file"],
    horizontal=True,
)

candidates = None

if source.startswith("Use bundled"):
    try:
        with open("sample_candidates.json") as f:
            candidates = json.load(f)
        st.success(f"Loaded {len(candidates)} candidates from sample_candidates.json")
    except FileNotFoundError:
        st.error("sample_candidates.json not found in this deployment.")
else:
    uploaded = st.file_uploader("Upload a JSON or JSONL file", type=["json", "jsonl"])
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

st.divider()

# ----------------------------------------------------------------
# Run ranking
# ----------------------------------------------------------------
st.subheader("2. Run the ranker")

top_n = st.slider("Number of top candidates to show", min_value=5, max_value=100, value=20, step=5)

if candidates and st.button("Rank candidates", type="primary"):
    start = time.time()
    with st.spinner("Scoring candidates..."):
        ranked = rank_candidates(candidates)
    elapsed = time.time() - start

    honeypot_count = sum(1 for c in candidates if is_honeypot(c))

    col1, col2, col3 = st.columns(3)
    col1.metric("Candidates scored", len(candidates))
    col2.metric("Honeypots filtered", honeypot_count)
    col3.metric("Runtime", f"{elapsed:.2f}s")

    st.divider()
    st.subheader(f"3. Top {top_n} results")

    rows = []
    for r in ranked[:top_n]:
        rows.append({
            "Rank": r["rank"],
            "Candidate ID": r["candidate_id"],
            "Score": r["score"],
            "Reasoning": r["reasoning"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download as CSV",
        data=csv,
        file_name="ranked_output.csv",
        mime="text/csv",
    )

    # ------------------------------------------------------------
    # Score breakdown for a single candidate
    # ------------------------------------------------------------
    st.divider()
    st.subheader("4. Inspect a candidate's score breakdown")

    id_to_candidate = {c["candidate_id"]: c for c in candidates}
    selected_id = st.selectbox(
        "Select a candidate ID from the ranked list above",
        [r["candidate_id"] for r in ranked[:top_n]],
    )

    if selected_id:
        cand = id_to_candidate[selected_id]
        career = score_career(cand)
        skills = score_skills(cand)
        behavioral = score_behavioral(cand)
        experience = score_experience(cand)
        profile = score_profile(cand)

        st.markdown(f"**{cand['profile']['current_title']}** at "
                    f"**{cand['profile']['current_company']}** "
                    f"({cand['profile']['years_of_experience']} yrs)")

        bcol1, bcol2, bcol3, bcol4, bcol5 = st.columns(5)
        bcol1.metric("Career (40%)", f"{career:.2f}")
        bcol2.metric("Skills (25%)", f"{skills:.2f}")
        bcol3.metric("Behavioral (20%)", f"{behavioral:.2f}")
        bcol4.metric("Experience (10%)", f"{experience:.2f}")
        bcol5.metric("Profile (5%)", f"{profile:.2f}")

        with st.expander("Full candidate JSON"):
            st.json(cand)

elif not candidates:
    st.info("Load candidates above, then click 'Rank candidates' to run the system.")

st.divider()
st.caption(
    "Pure Python standard library — no GPU, no network calls during ranking. "
    "Full source: [github.com/Shristi1611/redrob-intelligent-ranker]"
    "(https://github.com/Shristi1611/redrob-intelligent-ranker)"
)