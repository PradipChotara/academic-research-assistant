# pages/4_🔬_Advanced_Analysis.py

import streamlit as st
from core_engine import configure_llm, load_index, create_sub_question_engine

st.set_page_config(page_title="Advanced Analysis", page_icon="🔬")
st.title("🔬 Advanced Document Analysis")
st.info("This page uses a more advanced agent that can break down complex questions and compare information across multiple documents.", icon="💡")

# --- Load Index and LLM ---
index = load_index()
llm = configure_llm()

if index is None or llm is None:
    st.error("The core components are not loaded. Please go to the Home/Indexing page first.", icon="⚙️")
    st.stop()

# --- Initialize Sub-Question Engine ---
if "sub_question_engine" not in st.session_state:
    st.session_state.sub_question_engine = create_sub_question_engine(index)

sub_question_engine = st.session_state.sub_question_engine

if sub_question_engine is None:
    st.warning("Could not create the advanced engine. Please make sure at least one document is indexed.", icon="⚠️")
    st.stop()

# --- Chat History and User Input ---
if "advanced_messages" not in st.session_state:
    st.session_state.advanced_messages = [{"role": "assistant", "content": "Hello! I'm ready to answer complex, multi-step questions about your documents."}]

for message in st.session_state.advanced_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Ask a comparative question..."):
    st.session_state.advanced_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Decomposing question and querying sources... This may take longer."):
            response = sub_question_engine.query(prompt)
            st.write(response.response)
            
            # Display the generated sub-questions for transparency
            with st.expander("View thought process (Sub-Questions)"):
                for source_node in response.source_nodes:
                    st.write(source_node.metadata.get('sub_question'))
            
            st.session_state.advanced_messages.append({"role": "assistant", "content": response.response})