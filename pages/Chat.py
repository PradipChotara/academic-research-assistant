# pages/3_💬_App.py

import streamlit as st
from core_engine import configure_llm, load_index

st.set_page_config(page_title="App", page_icon="💬")
st.title("💬 Chat with the Research Assistant")

# --- Load Index and LLM ---
# This page is the only one that needs the heavy LLM.
index = load_index()
llm = configure_llm()

if index is None:
    st.error("No data index found. Please go to the 'Indexing' page and build the index first.", icon="⚙️")
    st.stop()

if llm is None:
    st.error("Language Model could not be loaded. This may be due to resource limitations. "
             "Please ensure the application is running on a machine with sufficient memory.", icon="🚨")
    st.stop()

# --- Initialize Chat Engine ---
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", llm=llm, verbose=True)

# --- Chat History and User Input ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm ready to answer questions about your documents."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            st.session_state.messages.append({"role": "assistant", "content": response.response})