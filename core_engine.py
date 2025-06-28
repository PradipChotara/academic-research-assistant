# core_engine.py

import os
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

# --- App Configuration ---
DATA_DIR = "./research_papers"
PERSIST_DIR = "./storage"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PERSIST_DIR, exist_ok=True)

# --- LlamaIndex Setup ---
@st.cache_resource(show_spinner="Connecting to AI models...")
def configure_ai():
    """Sets up the LlamaIndex settings and loads the Ollama models."""
    Settings.llm = Ollama(model="mistral", request_timeout=300.0)
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    print("AI Models configured.")

@st.cache_resource(show_spinner="Loading data index... This might take a moment.")
def load_index():
    """Loads or creates the LlamaIndex index."""
    if not os.listdir(PERSIST_DIR):
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    return index

def add_document_to_index(uploaded_file):
    """Saves an uploaded file and adds it to the index."""
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    document = SimpleDirectoryReader(input_files=[file_path]).load_data()[0]
    index = st.session_state.index # Get the index from session state
    index.insert_document(document)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    return f"'{uploaded_file.name}' added to index."

def delete_document_from_index(doc_id, file_name):
    """Deletes a document from the index and the file system."""
    index = st.session_state.index # Get the index from session state
    index.delete_ref_doc(doc_id, delete_from_docstore=True)
    
    file_path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    return f"'{file_name}' has been deleted."