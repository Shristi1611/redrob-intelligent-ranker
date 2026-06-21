import streamlit as st
import streamlit.components.v1 as components
import os
from shared_ui import inject_global_styles, render_sidebar_footer

inject_global_styles()
render_sidebar_footer()

st.markdown(
    '<div style="display:none; background:#1A1814; color:#F2F0E8; padding:10px 16px; '
    'border-radius:8px; font-size:13px; margin-bottom:16px;" '
    'class="mobile-sidebar-hint">'
    'On mobile, tap the arrow in the top-left corner to open the menu and load candidates.'
    '</div>'
    '<style>'
    '@media (max-width: 768px) { .mobile-sidebar-hint { display: block !important; } }'
    '</style>',
    unsafe_allow_html=True,
)

hero_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hero_component.html")
with open(hero_path, "r", encoding="utf-8") as f:
    hero_html = f.read()
components.html(hero_html, height=320, scrolling=False)

st.write("")
st.write("")

st.markdown('<p class="section-heading">About this system</p>', unsafe_allow_html=True)
st.markdown('<p class="section-title">How it ranks candidates</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        '<div class="candidate-banner">'
        '<span style="font-weight:700; color:#1A1814;">Career history first</span><br/>'
        '<span style="color:rgba(20,18,14,0.6); font-size:14px;">Skills only count when career history shows '
        'they were actually used. A profile listing a tool with no supporting work experience is discounted.</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        '<div class="candidate-banner">'
        '<span style="font-weight:700; color:#1A1814;">Honeypot detection</span><br/>'
        '<span style="color:rgba(20,18,14,0.6); font-size:14px;">Cross-validates stated experience against '
        'summed career history to catch data-consistency traps in the candidate pool.</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        '<div class="candidate-banner">'
        '<span style="font-weight:700; color:#1A1814;">Behavioral signals</span><br/>'
        '<span style="color:rgba(20,18,14,0.6); font-size:14px;">Weighs availability and platform engagement, '
        'response rate, notice period, recent activity, alongside fit.</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        '<div class="candidate-banner">'
        '<span style="font-weight:700; color:#1A1814;">No external dependencies</span><br/>'
        '<span style="color:rgba(20,18,14,0.6); font-size:14px;">Runs entirely on the Python standard library. '
        'No GPU, no network calls during ranking.</span>'
        '</div>',
        unsafe_allow_html=True,
    )

st.write("")
st.write("")
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)
st.markdown(
    '<div class="footer-bar">'
    'Use the sidebar to upload candidates and run the ranker.<br/>'
    '<a href="https://github.com/Shristi1611/redrob-intelligent-ranker" target="_blank">'
    'View source on GitHub</a>'
    '</div>',
    unsafe_allow_html=True,
)