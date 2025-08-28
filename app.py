import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.prompts import Prompt

# Load API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Initialize model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

st.title("📄 Resume Parser with LangChain + Gemini")

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        loader = PyPDFLoader(uploaded_file)
    elif file_type == "docx":
        loader = Docx2txtLoader(uploaded_file)
    elif file_type == "txt":
        loader = TextLoader(uploaded_file)
    else:
        st.error("❌ Unsupported file format.")
        loader = None

    if loader:
        docs = loader.load()
        resume_text = "\n".join([doc.page_content for doc in docs])

        st.subheader("📑 Extracted Resume Text")
        st.write(resume_text)

        prompt_template = """
        You are an AI Resume Parser. Extract the following details clearly:

        - Name
        - Email
        - Phone Number
        - Skills
        - Education
        - Work Experience

        Resume:
        {resume_text}
        """

        prompt = Prompt.from_template(prompt_template)

        response = llm.invoke(prompt.format(resume_text=resume_text))

        st.subheader("✅ Parsed Resume Information")
        st.write(response.content)
