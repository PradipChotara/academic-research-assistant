# pages/1_💬_Chat.py

import streamlit as st

st.set_page_config(page_title="Chat", page_icon="💬")
st.title("💬 Chat with Your Documents")

# Ensure the index is loaded and available in the session state
if "index" not in st.session_state:
    st.error("Index not loaded. Please go to the Home page to load the data first.")
    st.stop()

# Initialize chat engine and messages in session state
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = st.session_state.index.as_chat_engine(chat_mode="context", verbose=True)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Ask me anything about your documents."}]

# Display past chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Get user input and handle chat logic
if prompt := st.chat_input("Your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            st.session_state.messages.append({"role": "assistant", "content": response.response})