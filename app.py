# app.py

import streamlit as st

st.set_page_config(
    page_title="Home - Academic Research Assistant",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Academic Research Assistant")
st.write("---")
st.header("Welcome!")

st.info(
    """
    This application is your personal AI assistant for academic research.
    It allows you to manage a collection of papers and chat with an AI that uses them as its knowledge base.

    **How to use this app:**

    1.  **📄 Documents:** Go to the Documents page to upload the PDF files you want the AI to learn from. You can also delete papers you no longer need.

    2.  **⚙️ Indexing:** After uploading or deleting documents, go to the Indexing page. Click the button to build the AI's knowledge base. This step must be done anytime you change your documents.

    3.  **💬 App:** Once the index is built, navigate to the App page to start chatting with your research assistant!
    """,
    icon="ℹ️"
)