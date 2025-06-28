# pages/2_📄_Manage_Documents.py

import streamlit as st
import os
from core_engine import add_document_to_index, delete_document_from_index

st.set_page_config(page_title="Manage Documents", page_icon="📄")
st.title("📄 Manage Documents")

# Ensure the index is loaded and available in the session state
if "index" not in st.session_state:
    st.error("Index not loaded. Please go to the Home page to load the data first.")
    st.stop()

# --- UI for Document Management ---
st.subheader("Upload New Papers")
uploaded_files = st.file_uploader(
    "Upload PDF files here",
    type="pdf",
    accept_multiple_files=True
)
if st.button("Add to Index"):
    if uploaded_files:
        with st.spinner("Adding new document(s) to the index..."):
            for file in uploaded_files:
                feedback = add_document_to_index(file)
                st.success(feedback)
    else:
        st.warning("Please upload at least one file.")

st.divider()

st.subheader("Currently Indexed Papers")
docstore = st.session_state.index.docstore.docs
if not docstore:
    st.write("No papers have been indexed yet.")
else:
    for doc_id, doc in docstore.items():
        file_name = doc.metadata.get('file_name', 'Unknown')
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text(file_name)
        with col2:
            if st.button("Delete", key=f"delete_{doc_id}", type="primary"):
                with st.spinner(f"Deleting {file_name}..."):
                    feedback = delete_document_from_index(doc_id, file_name)
                    st.success(feedback)
                    st.rerun()