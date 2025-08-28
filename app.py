# resume_parser_app.py

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.prompts import Prompt
import json

# -----------------------
# Load API Key
# -----------------------
# First check Streamlit secrets (works for deployment)
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
else:
    # Fallback: load from .env (useful for local development)
    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# -----------------------
# App UI
# -----------------------
st.title("📄 Resume Parser with Google Generative AI")

uploaded_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1]

    # Save file temporarily
    temp_path = f"temp.{file_type}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Load document
    if file_type == "pdf":
        loader = PyPDFLoader(temp_path)
    elif file_type == "docx":
        loader = Docx2txtLoader(temp_path)
    else:
        loader = TextLoader(temp_path)

    docs = loader.load()
    resume_text = " ".join([d.page_content for d in docs])

    # -----------------------
    # Prompt for structured parsing
    # -----------------------
    template = """
    Extract the following information from the resume text:

    - Full Name
    - Email
    - Phone Number
    - Skills
    - Technical Skills
    - Education
    - Work Experience
    - Certifications (if any)

    Resume Text:
    {resume}

    Format output as JSON.
    """

    prompt = Prompt.from_template(template)

    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

    response = llm.invoke(prompt.format(resume=resume_text))

    try:
        parsed = json.loads(response.content)
    except:
        parsed = {"error": "Could not parse into JSON", "raw_response": response.content}

    st.subheader("📌 Extracted Resume Information")
    st.json(parsed)
