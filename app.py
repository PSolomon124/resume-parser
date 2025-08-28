# app.py
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import tempfile
import os

# Load API key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

# Define a prompt template for parsing resumes
prompt_template = PromptTemplate(
    input_variables=["resume_text"],
    template="""
You are a professional Resume Parser. Extract the following information from the resume text:

- Full Name
- Email
- Phone
- Education
- Skills
- Work Experience
- Certifications (if any)

Resume Text:
{resume_text}

Provide the extracted information in a structured JSON format.
"""
)

# Build LLM chain
chain = LLMChain(llm=llm, prompt=prompt_template)

st.title("📄 AI Resume Parser")
st.write("Upload a resume (PDF, DOCX, or TXT) and let AI parse it into structured data.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    # Load file depending on type
    if uploaded_file.name.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif uploaded_file.name.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        loader = TextLoader(file_path)

    documents = loader.load()
    resume_text = "\n".join([doc.page_content for doc in documents])

    st.subheader("📑 Extracted Text Preview")
    st.text_area("Resume Text", resume_text[:1500] + "..." if len(resume_text) > 1500 else resume_text, height=250)

    # Parse with LLM
    with st.spinner("Parsing resume with AI..."):
        result = chain.run(resume_text=resume_text)

    st.subheader("✅ Parsed Resume Data")
    st.json(result)
