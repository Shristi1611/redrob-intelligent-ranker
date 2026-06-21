import streamlit as st


def inject_global_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    * { font-family: 'Sora', sans-serif; }

    .stApp { background: #EFEBE2; }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent;
    }
    header[data-testid="stHeader"] button {
        background: #1A1814 !important;
        border-radius: 8px !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    header[data-testid="stHeader"] button svg {
        color: #F2F0E8 !important;
        fill: #F2F0E8 !important;
    }
    .block-container { padding-top: 2.5rem; max-width: 880px; }

    section[data-testid="stSidebar"] {
        background: #1A1814;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] * { color: #DAD4C6 !important; }
    section[data-testid="stSidebar"] .sidebar-logo {
        font-size: 18px;
        font-weight: 700;
        color: #F2F0E8 !important;
        letter-spacing: -0.01em;
        margin-bottom: 4px;
    }
    section[data-testid="stSidebar"] .sidebar-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10.5px;
        letter-spacing: 0.06em;
        color: rgba(218,212,198,0.5) !important;
        text-transform: uppercase;
        margin-bottom: 24px;
    }
    section[data-testid="stSidebar"] .sidebar-footer {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        color: rgba(218,212,198,0.35) !important;
        position: fixed;
        bottom: 24px;
        line-height: 1.7;
    }
    div[data-testid="stSidebarNav"] { padding-top: 4px; }

    .section-heading {
        font-size: 12.5px;
        font-weight: 600;
        letter-spacing: 0.06em;
        color: rgba(20,18,14,0.45);
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1A1814;
        letter-spacing: -0.01em;
        margin: 4px 0 18px 0;
    }

    .candidate-banner {
        background: #FFFFFF;
        border: 1px solid rgba(20,18,14,0.1);
        border-radius: 8px;
        padding: 18px 22px;
        margin-top: 16px;
    }

    hr.divider {
        border: none;
        height: 1px;
        background: rgba(20,18,14,0.1);
        margin: 36px 0;
    }

    .footer-bar {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11.5px;
        color: rgba(20,18,14,0.4);
        border-top: 1px solid rgba(20,18,14,0.1);
        padding-top: 18px;
        margin-top: 12px;
        line-height: 1.8;
    }
    .footer-bar a { color: #1A1814; text-decoration: underline; text-underline-offset: 2px; }
    .footer-bar a:hover { color: rgba(20,18,14,0.6); }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(20,18,14,0.1);
        border-radius: 8px;
        overflow: hidden;
    }
    .stButton button {
        background: #1A1814;
        color: #F2F0E8;
        border: none;
        font-weight: 600;
        border-radius: 100px;
        padding: 10px 26px;
        transition: opacity 0.2s ease;
    }
    .stButton button:hover { opacity: 0.82; }
    .stButton button:disabled { background: rgba(20,18,14,0.15); color: rgba(20,18,14,0.35); }
    div[data-baseweb="select"] > div, .stTextInput input {
        background: #FFFFFF !important;
        border-color: rgba(20,18,14,0.15) !important;
        border-radius: 6px !important;
    }
    div[role="radiogroup"] label {
        background: #FFFFFF;
        border: 1px solid rgba(20,18,14,0.12);
        border-radius: 100px;
        padding: 6px 18px !important;
    }
    .stAlert {
        background: rgba(20,18,14,0.04) !important;
        border: 1px solid rgba(20,18,14,0.12) !important;
        border-radius: 6px !important;
    }

    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #1A1814 !important;
        border-color: #1A1814 !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
        background: #1A1814 !important;
    }
    div[data-testid="stTickBar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_footer():
    st.sidebar.markdown(
        '<div class="sidebar-footer">Pure Python standard library<br/>No GPU, no network calls<br/>'
        '100,000 candidates in under 40s</div>',
        unsafe_allow_html=True,
    )