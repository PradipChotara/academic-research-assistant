# core_engine.py

import os
import shutil
import streamlit as st
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from ollama import ResponseError

# --- App Configuration ---
DATA_DIR = "./research_papers"
PERSIST_DIR = "./storage"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PERSIST_DIR, exist_ok=True)

# --- LlamaIndex Core Functions ---

@st.cache_resource(show_spinner="Connecting to Embedding Model...")
def configure_embed_model():
    """Sets up the embedding model only. This is lightweight."""
    try:
        Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
        print("Embedding Model configured.")
        return True
    except Exception as e:
        st.error(f"Failed to configure embedding model: {e}", icon="🚨")
        return False

@st.cache_resource(show_spinner="Connecting to Language Model... This may take a while.")
def configure_llm():
    """Sets up the language model. This is the heavy operation."""
    try:
        Settings.llm = Ollama(model="mistral", request_timeout=300.0)
        print("Language Model configured.")
        return Settings.llm
    except ResponseError as e:
        st.error(f"Failed to load the language model: {e}", icon="🚨")
        st.info("The AI model may require more resources (RAM) than are available. "
                "Chat functionality will be disabled.")
        return None

def rebuild_index():
    """Deletes old index and builds a new one from documents in DATA_DIR."""
    # Delete old storage directory
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    os.makedirs(PERSIST_DIR, exist_ok=True)

    # Load documents and create the index
    documents = SimpleDirectoryReader(DATA_DIR).load_data()
    if not documents:
        return "No documents found to index."
    
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    return f"Successfully built index for {len(documents)} document(s)."

def load_index():
    """Loads the existing index from storage."""
    if not os.listdir(PERSIST_DIR):
        return None # No index exists
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    return load_index_from_storage(storage_context)