# app.py

import streamlit as st
from core_engine import configure_ai, load_index

st.set_page_config(
    page_title="Home - Academic Research Assistant",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Academic Research Assistant")
st.info(
    "Welcome! This application helps you chat with and manage your academic papers. "
    "Navigate to the pages in the sidebar to get started.",
    icon="ℹ️"
)

# --- Initialize AI Engine and Index ---
# This runs once and caches the result for the entire user session
configure_ai()
index = load_index()

# Store the loaded index in the session state to be accessible across pages
if "index" not in st.session_state:
    st.session_state.index = index

st.success("AI Engine and Data Index are loaded and ready. Please proceed to a page on the left.", icon="✅")

# --- Optional: Display some stats or info on the homepage ---
with st.expander("Show Document Stats"):
    if "index" in st.session_state:
        num_docs = len(st.session_state.index.docstore.docs)
        st.write(f"There are currently **{num_docs}** documents indexed.")