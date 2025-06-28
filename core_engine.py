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
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.vector_stores import MetadataFilter, ExactMatchFilter

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

# --- MODIFIED FUNCTION for Advanced Engine ---

@st.cache_resource(show_spinner="Creating advanced analysis engine...")
def create_sub_question_engine(_index): # CHANGED: Argument name from 'index' to '_index'
    """Creates a SubQuestionQueryEngine from the documents in the index."""
    docstore = _index.docstore.docs # CHANGED: Using '_index'
    if not docstore:
        return None

    # Create a list of "expert tools," one for each document
    query_engine_tools = []
    for doc_id, doc in docstore.items():
        file_name = doc.metadata.get('file_name', 'Unknown Document')
        
        # Create a retriever that only looks at this one document
        retriever = _index.as_retriever( # CHANGED: Using '_index'
            filters=MetadataFilter(filters=[ExactMatchFilter(key="file_name", value=file_name)])
        )
        
        # Create a query engine for this single document
        doc_query_engine = _index.as_query_engine(retriever=retriever) # CHANGED: Using '_index'

        # Create the tool. The description is crucial for the AI to know when to use it.
        query_engine_tool = QueryEngineTool(
            query_engine=doc_query_engine,
            metadata=ToolMetadata(
                name=f"tool_{file_name.replace(' ', '_').replace('.pdf', '')}",
                description=(
                    "This tool is an expert on the research paper titled "
                    f"'{file_name}'. Use it to answer specific questions about this paper's "
                    "content, methodology, findings, etc."
                ),
            ),
        )
        query_engine_tools.append(query_engine_tool)

    # Create the master Sub-Question Query Engine from the list of expert tools
    return SubQuestionQueryEngine.from_defaults(query_engine_tools=query_engine_tools)