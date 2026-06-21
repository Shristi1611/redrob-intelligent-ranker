import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ranker import (
    rank_candidates,
    is_honeypot,
    score_career,
    score_skills,
    score_behavioral,
    score_experience,
    score_profile,
)
from shared_ui import inject_global_styles, render_sidebar_footer

inject_global_styles()
render_sidebar_footer()

candidates = st.session_state.get("candidates")

st.markdown('<p class="section-heading">Step 02</p>', unsafe_allow_html=True)
st.markdown('<p class="section-title">Run the ranker</p>', unsafe_allow_html=True)

if candidates is None:
    st.info("No candidates loaded yet. Go to the Upload page in the sidebar first.")
else:
    top_n = st.slider("Candidates to display", min_value=5, max_value=100, value=20, step=5)
    run_clicked = st.button("Rank candidates", type="primary")

    # Storing results in session_state means selecting a candidate from the
    # dropdown below (which triggers a rerun) does not collapse this section
    # back to the unranked state. Only a fresh button click re-runs ranking.
    if run_clicked:
        start = time.time()
        with st.spinner("Scoring career history, skills, and availability signals..."):
            ranked = rank_candidates(candidates)
        elapsed = time.time() - start
        st.session_state["ranked"] = ranked
        st.session_state["elapsed"] = elapsed
        st.session_state["top_n"] = top_n

    st.write("")

    if "ranked" in st.session_state:
        ranked = st.session_state["ranked"]
        elapsed = st.session_state["elapsed"]
        top_n = st.session_state.get("top_n", top_n)

        honeypot_count = sum(1 for c in candidates if is_honeypot(c))

        results_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results_component.html")
        with open(results_path, "r", encoding="utf-8") as f:
            results_html = f.read()

        metrics_data = [
            {"value": len(candidates), "label": "Candidates scored"},
            {"value": honeypot_count, "label": "Honeypots filtered"},
            {"value": f"{elapsed:.2f}s", "label": "Runtime"},
        ]

        st.markdown('<hr class="divider"/>', unsafe_allow_html=True)
        components.html(
            results_html.replace(
                "__DATA_PLACEHOLDER__",
                json.dumps({"metrics": metrics_data, "scores": []})
            ),
            height=160,
            scrolling=False,
        )

        st.write("")
        st.markdown(f'<p class="section-title" style="font-size:17px;">Top {top_n} candidates</p>', unsafe_allow_html=True)

        rows = [{
            "Rank": r["rank"],
            "Candidate ID": r["candidate_id"],
            "Score": r["score"],
            "Reasoning": r["reasoning"],
        } for r in ranked[:top_n]]

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True, height=min(60 + top_n * 35, 600))

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="ranked_output.csv", mime="text/csv")

        st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

        st.markdown('<p class="section-heading">Step 03</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Inspect a score breakdown</p>', unsafe_allow_html=True)

        id_to_candidate = {c["candidate_id"]: c for c in candidates}
        selected_id = st.selectbox(
            "Candidate",
            [r["candidate_id"] for r in ranked[:top_n]],
            label_visibility="collapsed",
        )

        if selected_id:
            cand = id_to_candidate[selected_id]
            career = score_career(cand)
            skills = score_skills(cand)
            behavioral = score_behavioral(cand)
            experience = score_experience(cand)
            profile = score_profile(cand)

            st.markdown(
                f'<div class="candidate-banner">'
                f'<span style="font-size:16px; font-weight:700; color:#1A1814;">{cand["profile"]["current_title"]}</span>'
                f'<span style="color:rgba(20,18,14,0.4);"> at </span>'
                f'<span style="font-size:16px; font-weight:700; color:#1A1814;">{cand["profile"]["current_company"]}</span>'
                f'<br/><span style="font-family:JetBrains Mono, monospace; font-size:12px; color:rgba(20,18,14,0.4);">'
                f'{cand["profile"]["years_of_experience"]} years experience</span></div>',
                unsafe_allow_html=True,
            )

            score_data = {"metrics": [], "scores": [
                {"name": "CAREER", "weight": "40%", "val": career},
                {"name": "SKILLS", "weight": "25%", "val": skills},
                {"name": "BEHAVIORAL", "weight": "20%", "val": behavioral},
                {"name": "EXPERIENCE", "weight": "10%", "val": experience},
                {"name": "PROFILE", "weight": "5%", "val": profile},
            ]}
            components.html(
                results_html.replace("__DATA_PLACEHOLDER__", json.dumps(score_data)),
                height=150,
                scrolling=False,
            )

            with st.expander("View full candidate JSON"):
                st.json(cand)
    else:
        st.info(f"{len(candidates)} candidates loaded. Click 'Rank candidates' to run the system.")