# app.py

import streamlit as st
from core_engine import configure_embed_model, configure_llm, load_index

st.set_page_config(
    page_title="Home - Academic Research Assistant",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Academic Research Assistant")
st.info(
    "Welcome! Please wait a moment while the core components are loaded...",
    icon="ℹ️"
)

# --- Initialize AI Engine and Index in a robust way ---
# We use st.session_state to ensure this initialization happens only once per session.
if "app_initialized" not in st.session_state:
    # 1. Configure the lightweight embedding model
    configure_embed_model()
    
    # 2. Load the data index
    index = load_index()
    if index is not None:
        st.session_state.index = index
        # 3. Configure the heavy language model (LLM)
        llm = configure_llm()
        if llm:
            st.session_state.llm = llm
            # 4. Create the basic chat engine
            st.session_state.chat_engine = index.as_chat_engine(
                chat_mode="context", llm=llm, verbose=True
            )
            st.session_state.app_initialized = True
        else:
            st.error("Failed to load Language Model. Chat functionality will be disabled.")
            st.session_state.app_initialized = False
    else:
        st.warning("No data index found. Please go to the 'Indexing' page to build one.")
        st.session_state.app_initialized = False

if st.session_state.get("app_initialized"):
    st.success("All components loaded successfully! Please navigate to a page on the left.", icon="✅")
else:
    st.error("Application could not be initialized. Please check the setup and resource availability.")