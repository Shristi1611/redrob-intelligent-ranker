import streamlit as st

st.set_page_config(page_title="Redrob Intelligent Ranker", layout="wide")

home = st.Page("pages/Home.py", title="Home", default=True)
upload = st.Page("pages/Upload.py", title="Upload")
results = st.Page("pages/Results.py", title="Results")

pg = st.navigation([home, upload, results])
pg.run()