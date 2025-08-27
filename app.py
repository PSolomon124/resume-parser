import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.prompts import PromptTemplate

# -----------------------------
# Streamlit App Config
# -----------------------------
st.set_page_config(page_title="AI Resume Parser", page_icon="📄", layout="centered")

st.title("📄 AI Resume Parser")
st.write("Upload your resume and extract structured details like **Name, Email, Skills, Education, Experience, Technologies**.")

# -----------------------------
# Load Google Gemini API Key
# -----------------------------
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("❌ GOOGLE_API_KEY not found. Please add it in Streamlit Secrets.")
    st.stop()

# Initialize Google Generative AI (Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",   # ✅ Fixed model name
    google_api_key=st.secrets["GOOGLE_API_KEY"],
    temperature=0.2
)

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1].lower()

    # Save temp file for processing
    temp_file_path = f"temp.{file_type}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    # Extract text depending on file type
    if file_type == "pdf":
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        resume_text = " ".join([doc.page_content for doc in documents])
    elif file_type == "docx":
        loader = Docx2txtLoader(temp_file_path)
        documents = loader.load()
        resume_text = " ".join([doc.page_content for doc in documents])
    else:  # txt
        loader = TextLoader(temp_file_path)
        documents = loader.load()
        resume_text = " ".join([doc.page_content for doc in documents])

    st.subheader("📑 Extracted Raw Resume Text")
    st.write(resume_text[:1000] + "...")  # show only first 1000 chars

    # -----------------------------
    # LLM Prompt for Resume Parsing
    # -----------------------------
    prompt_template = """
    You are an expert Resume Parser. Extract the following structured details from the resume text:

    Resume Text:
    {resume_text}

    Provide output strictly in JSON format with these fields:
    {{
      "name": "",
      "email": "",
      "phone": "",
      "skills": [],
      "technologies": [],
      "education": [],
      "experience": []
    }}
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["resume_text"])

    # Run parsing
    with st.spinner("🔍 Parsing resume with AI..."):
        response = llm.invoke(prompt.format(resume_text=resume_text))

    # Display result
    st.subheader("✅ Parsed Resume Data")
    st.json(response.content)
