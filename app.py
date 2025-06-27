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

# --- NEW IMPORTS FOR ERROR HANDLING ---
from httpx import ReadTimeout
from ollama import ResponseError

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
@st.cache_resource(show_spinner="Connecting to AI models...")
def configure_ai():
    """Sets up the LlamaIndex settings and loads the Ollama models."""
    Settings.llm = Ollama(model="mistral", request_timeout=300.0)
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

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
    return index

# --- Main App Logic ---
try:
    configure_ai()
    index = load_and_index_data()
except Exception as e:
    st.error(f"Failed to initialize the application. Please check your setup. Error: {e}", icon="🚨")
    st.stop() # Stop the app if setup fails

# Initialize the chat engine in Streamlit's session state if it doesn't exist
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", verbose=True)

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

# --- MODIFIED SECTION: Get user input and handle errors ---
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # If the last message is not from the assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat_engine.chat(prompt)
                    
                    response_str = response.response
                    sources = "\n".join([f"- {os.path.basename(node.metadata.get('file_name', 'N/A'))} (Page: {node.metadata.get('page_label', 'N/A')})" for node in response.source_nodes])
                    
                    # Display the response and sources
                    st.write(response_str)
                    st.info(f"Sources:\n{sources}")
                    
                    # Add the full assistant response to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_str
                    })

                # --- Catch specific, known errors and display friendly messages ---
                except ReadTimeout:
                    error_message = "The AI model took too long to respond. This can happen on very complex questions. Please try asking a simpler question or try again."
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

                except ResponseError as e:
                    error_text = str(e).lower()
                    if "memory" in error_text:
                        error_message = "The AI model ran out of memory. The server may be under heavy load or the question is too complex. Please try again later."
                    elif "not found" in error_text:
                        error_message = "The AI model specified is not available on the server. Please contact the administrator."
                    else:
                        error_message = f"An error occurred with the AI model: {e}"
                    
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                
                # --- Catch any other unexpected errors ---
                except Exception as e:
                    error_message = f"An unexpected error occurred: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})