# pages/2_⚙️_Indexing.py

import streamlit as st
import os
import time
from core_engine import configure_embed_model, rebuild_index

# --- NEW IMPORTS for Timezone Conversion ---
from datetime import datetime
from zoneinfo import ZoneInfo

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
            st.rerun() # Rerun to update the timestamp below immediately

st.divider()

# --- MODIFIED SECTION: Display Index Status with Timezone Conversion ---
st.subheader("Current Index Status")
if not os.listdir(PERSIST_DIR):
    st.write("No index has been built yet.")
else:
    try:
        # 1. Get the modification time as a UTC timestamp from the file system
        mod_time_timestamp = os.path.getmtime(PERSIST_DIR)
        
        # 2. Convert it to a timezone-aware datetime object in UTC
        utc_time = datetime.fromtimestamp(mod_time_timestamp, tz=ZoneInfo("UTC"))
        
        # 3. Convert the UTC time to Indian Standard Time (IST)
        india_time = utc_time.astimezone(ZoneInfo("Asia/Kolkata"))
        
        # 4. Format it into a user-friendly string
        formatted_time = india_time.strftime('%a, %d %b %Y, %I:%M:%S %p %Z')
        
        st.write(f"Index was last built on: **{formatted_time}**")
        
    except Exception as e:
        st.error(f"Could not read index status: {e}")