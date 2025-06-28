# pages/1_📄_Documents.py

import streamlit as st
import os

st.set_page_config(page_title="Manage Documents", page_icon="📄")
st.title("📄 Document Management")
st.info("Here you can upload new research papers or delete existing ones. "
        "Remember to go to the 'Indexing' page to update the AI's knowledge base after making changes.", icon="💡")

DATA_DIR = "./research_papers"

# --- UI for Document Management ---

st.subheader("Upload New Papers")
uploaded_files = st.file_uploader(
    "Upload your PDF files here. They will be saved in the 'research_papers' folder.",
    type="pdf",
    accept_multiple_files=True
)

if st.button("Save Uploaded Files"):
    if uploaded_files:
        saved_count = 0
        with st.spinner("Saving files..."):
            for uploaded_file in uploaded_files:
                file_path = os.path.join(DATA_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_count += 1
        st.success(f"Successfully saved {saved_count} new paper(s).")
    else:
        st.warning("Please upload at least one file before saving.")

st.divider()

st.subheader("Current Document Library")
if not os.listdir(DATA_DIR):
    st.write("No papers have been uploaded yet.")
else:
    for file_name in os.listdir(DATA_DIR):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text(file_name)
        with col2:
            if st.button("Delete", key=f"delete_{file_name}", type="primary"):
                os.remove(os.path.join(DATA_DIR, file_name))
                st.success(f"'{file_name}' has been deleted.")
                st.rerun()