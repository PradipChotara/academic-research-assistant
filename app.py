import streamlit as st
import os
import textwrap
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# --- App Configuration ---
st.set_page_config(
    page_title="Academic Research Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("📚 Personalized Academic Research Assistant")
st.info("Ask questions about the research papers you've uploaded. The assistant will use them as its knowledge source.", icon="ℹ️")

# --- Model and Path Configuration ---
DATA_DIR = "./research_papers"
PERSIST_DIR = "./storage"

# --- LlamaIndex Setup (Cached for Performance) ---
# Using Streamlit's caching to load models and data only once.

@st.cache_resource(show_spinner="Connecting to AI models...")
def configure_ai():
    """Sets up the LlamaIndex settings and loads the Ollama models."""
    Settings.llm = Ollama(model="mistral", request_timeout=300.0)
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    print("AI Models configured.")

@st.cache_resource(show_spinner="Loading and indexing your documents... This might take a moment.")
def load_and_index_data():
    """Loads documents and creates or loads the LlamaIndex index."""
    if not os.path.exists(PERSIST_DIR):
        st.write("Index not found. Creating a new one. This will take a few minutes...")
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        st.success("New index created and saved successfully!", icon="✅")
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        # Optional: Add logic here to refresh the index if new documents are added
        # For now, we assume the index is up-to-date for simplicity.
    return index

# --- Main App Logic ---
configure_ai()
index = load_and_index_data()

# Initialize the chat engine in Streamlit's session state if it doesn't exist
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="context",
        verbose=True
    )

# Initialize the chat messages history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your research assistant. How can I help you analyze your documents?"
    }]

# Display past chat messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Get user input from the chat input box at the bottom
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # If the last message is not from the assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chat_engine.stream_chat(prompt)
                
                # Stream the response to the UI
                response_str = ""
                response_container = st.empty()
                for token in response.response_gen:
                    response_str += token
                    response_container.markdown(response_str)

                # Display sources after the response is complete
                sources = "\n".join([f"- {os.path.basename(node.metadata.get('file_name', 'N/A'))} (Page: {node.metadata.get('page_label', 'N/A')})" for node in response.source_nodes])
                st.info(f"Sources:\n{sources}")
                
                # Add the full assistant response to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_str
                })