import os
import textwrap
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage
)
# We need the ChatMemoryBuffer to store the conversation history
from llama_index.core.memory import ChatMemoryBuffer

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# --- Configuration using Local Ollama Models ---
# Using Mistral, with a longer timeout
Settings.llm = Ollama(model="mistral", request_timeout=300.0) 
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# --- Directory Definitions ---
PERSIST_DIR = "./storage"
DATA_DIR = "./research_papers"

def main():
    """
    The main function to run the academic research assistant.
    This version automatically updates the index and has conversational memory.
    """
    # --- Load documents ---
    print("Loading documents...")
    documents = SimpleDirectoryReader(DATA_DIR).load_data()
    print(f"Loaded {len(documents)} documents.")

    # --- Index Creation or Loading/Updating ---
    if not os.path.exists(PERSIST_DIR):
        # If index does not exist, create it from scratch
        print(f"Index not found. Creating a new index...")
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("Index created and saved successfully.")
    else:
        # If index exists, load it and check for updates
        print(f"Loading existing index from '{PERSIST_DIR}'...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        print("Index loaded successfully.")
        
        print("Checking for new documents and updating index...")
        refreshed_documents = index.refresh_ref_docs(documents)
        if refreshed_documents[0]:
             index.storage_context.persist(persist_dir=PERSIST_DIR)
             print("Index has been updated with new documents.")
        else:
             print("Index is already up-to-date.")


    # Create a memory buffer to hold the conversation history
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

    # Create a chat engine from the index, with memory and a system prompt
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=(
            "You are a helpful and friendly academic research assistant. "
            "You must answer the user's questions based on the context of the provided research papers."
        ),
    )


    # --- Interactive Query Loop ---
    print("\n--- Welcome to your Personalized Academic Research Assistant! ---")
    print("Ask a question about your research papers. Type 'exit' or 'quit' to quit.")
    
    while True:
        query_str = input("\nYour Question: ")
        if query_str.lower() in ['exit', 'quit']:
            break
        
        response = chat_engine.chat(query_str)
        
        print("\nAssistant's Answer:")
        print(textwrap.fill(str(response), 100))
        
        print("\nSources:")
        for node in response.source_nodes:
            print(f"- {node.metadata.get('file_name', 'N/A')} (Page: {node.metadata.get('page_label', 'N/A')})")

if __name__ == "__main__":
    main()