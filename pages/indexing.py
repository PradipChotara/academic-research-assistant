# pages/2_⚙️_Indexing.py

import streamlit as st
import os
import time
from core_engine import configure_embed_model, rebuild_index

st.set_page_config(page_title="Indexing", page_icon="⚙️")
st.title("⚙️ Index Your Documents")
st.info("Click the button below to build the AI's knowledge base from your uploaded documents. "
        "This process needs to be run whenever you add or remove papers.", icon="💡")

DATA_DIR = "./research_papers"
PERSIST_DIR = "./storage"

# --- Embedding Model Configuration ---
# This is lightweight and can run on any machine.
if not configure_embed_model():
    st.error("Embedding model could not be configured. Please check your setup.")
    st.stop()

# --- Indexing UI ---

if st.button("Re-build Index From Scratch", type="primary"):
    if not os.listdir(DATA_DIR):
        st.error("No documents found in the 'research_papers' folder. Please upload documents first.", icon="⚠️")
    else:
        with st.spinner("Building index... This may take a while depending on the number of documents."):
            feedback = rebuild_index()
            st.success(feedback, icon="✅")

st.divider()

# --- Display Index Status ---
st.subheader("Current Index Status")
if not os.listdir(PERSIST_DIR):
    st.write("No index has been built yet.")
else:
    try:
        mod_time_timestamp = os.path.getmtime(PERSIST_DIR)
        mod_time = time.ctime(mod_time_timestamp)
        st.write(f"Index was last built on: **{mod_time}**")
    except Exception as e:
        st.error(f"Could not read index status: {e}")