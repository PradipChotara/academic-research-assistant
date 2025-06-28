# pages/chat.py

import streamlit as st

st.set_page_config(page_title="Chat", page_icon="💬")
st.title("💬 Chat with the Research Assistant")

# --- Check for initialization ---
if "chat_engine" not in st.session_state:
    st.error("Chat engine is not ready. Please go to the Home page to initialize the application first.", icon="🏠")
    st.stop()

# --- Add a button to clear chat history ---
with st.sidebar:
    st.header("Controls")
    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! The chat has been cleared. How can I help?"}]
        st.session_state.chat_engine.reset()
        st.rerun()

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