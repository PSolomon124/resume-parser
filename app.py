import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="centered")

st.title("📄 AI Resume Parser")
st.write("Upload your resume (PDF, DOCX, or TXT) and I’ll parse the content for you.")

# Upload file
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

if uploaded_file:
    # Save file temporarily
    temp_path = os.path.join("temp_" + uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Choose loader based on file type
    file_ext = uploaded_file.name.split(".")[-1].lower()

    if file_ext == "pdf":
        loader = PyPDFLoader(temp_path)
    elif file_ext == "docx":
        loader = Docx2txtLoader(temp_path)
    elif file_ext == "txt":
        loader = TextLoader(temp_path)
    else:
        st.error("❌ Unsupported file format")
        os.remove(temp_path)
        st.stop()

    # Load document
    docs = loader.load()

    # Show output
    st.success("✅ Resume loaded successfully!")
    st.subheader("Extracted Content (Preview)")
    st.write(docs[0].page_content[:1000])  # Preview first 1000 chars

    # Clean up (optional)
    os.remove(temp_path)
