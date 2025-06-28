# core_engine.py

import os
import shutil
import streamlit as st
import re # <-- NEW: Import the regular expression library for cleaning names

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine, RetrieverQueryEngine
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter

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
        return True
    except Exception as e:
        st.error(f"Failed to configure embedding model: {e}", icon="🚨")
        return False

@st.cache_resource(show_spinner="Connecting to Language Model...")
def configure_llm():
    """Sets up the language model. This is the heavy operation."""
    try:
        Settings.llm = Ollama(model="mistral", request_timeout=300.0)
        return Settings.llm
    except ResponseError:
        return None

def rebuild_index():
    """Deletes old index and builds a new one from documents in DATA_DIR."""
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    os.makedirs(PERSIST_DIR, exist_ok=True)
    documents = SimpleDirectoryReader(DATA_DIR).load_data()
    if not documents:
        return "No documents found to index."
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    return f"Successfully built index for {len(index.docstore.docs)} document chunks."

def load_index():
    """Loads the existing index from storage."""
    if not os.listdir(PERSIST_DIR):
        return None
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    return load_index_from_storage(storage_context)

@st.cache_resource(show_spinner="Creating advanced analysis engine...")
def create_sub_question_engine(_index):
    """Creates a SubQuestionQueryEngine from the documents in the index."""
    docstore = _index.docstore.docs
    if not docstore:
        return None

    query_engine_tools = []
    for doc_id, doc in docstore.items():
        file_name = doc.metadata.get('file_name', 'Unknown Document')
        
        # --- MODIFIED SECTION: Create a clean, predictable tool name ---
        # 1. Remove the .pdf extension
        base_name = file_name.replace('.pdf', '')
        # 2. Replace all non-alphanumeric characters with underscores
        sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)

        retriever = _index.as_retriever(
            filters=MetadataFilters(filters=[ExactMatchFilter(key="file_name", value=file_name)])
        )
        
        doc_query_engine = RetrieverQueryEngine(retriever=retriever)

        query_engine_tool = QueryEngineTool(
            query_engine=doc_query_engine,
            metadata=ToolMetadata(
                # Use the new sanitized name
                name=sanitized_name,
                description=(
                    "This tool is an expert on the research paper titled "
                    f"'{file_name}'. Use it to answer specific questions about this paper's "
                    "content, methodology, findings, etc."
                ),
            ),
        )
        query_engine_tools.append(query_engine_tool)

    return SubQuestionQueryEngine.from_defaults(query_engine_tools=query_engine_tools)