import os
import textwrap
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage
)
# --- NEW IMPORTS for Ollama ---
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# --- Configuration using Local Ollama Models ---
# Use the local models you downloaded with Ollama
Settings.llm = Ollama(model="mistral", request_timeout=60.0)
# Settings.llm = Ollama(model="gemma:2b", request_timeout=60.0)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# --- NO OTHER CHANGES NEEDED BELOW THIS LINE ---

# Define the directory for storing the index and the source papers
PERSIST_DIR = "./storage"
DATA_DIR = "./research_papers"


def main():
    """
    The main function to run the academic research assistant.
    """
    # --- Index Creation or Loading ---
    if not os.path.exists(PERSIST_DIR):
        print(f"Index not found. Creating a new index from documents in '{DATA_DIR}'...")
        # Load the documents from the specified directory
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        
        # Create the vector store index from the documents
        # This will now use your local Ollama embedding model (free)
        index = VectorStoreIndex.from_documents(documents)
        
        # Persist the index to disk for future use
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("Index created and saved successfully.")
    else:
        print(f"Loading existing index from '{PERSIST_DIR}'...")
        # Load the existing index from the storage context
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        print("Index loaded successfully.")

    # --- Query Engine Setup ---
    # Create a query engine with source citation capabilities
    query_engine = index.as_query_engine(
        similarity_top_k=3,
        response_mode="compact"
    )

    # --- Interactive Query Loop ---
    print("\n--- Welcome to your Personalized Academic Research Assistant! ---")
    print("Ask a question about your research papers. Type 'exit' to quit.")
    
    while True:
        query_str = input("\nYour Question: ")
        if query_str.lower() == 'exit':
            break
        
        # This will now use your local Mistral model for generating answers (free)
        response = query_engine.query(query_str)
        
        # Print the response with proper formatting
        print("\nAssistant's Answer:")
        print(textwrap.fill(str(response), 100))
        
        # Print the source nodes for citation
        print("\nSources:")
        for node in response.source_nodes:
            # The 'file_name' metadata holds the name of the source PDF
            print(f"- {node.metadata.get('file_name', 'N/A')} (Page: {node.metadata.get('page_label', 'N/A')})")

if __name__ == "__main__":
    # Ensure Ollama application is running before starting the script
    print("Make sure the Ollama application is running on your desktop.")
    main()