# app.py
import streamlit as st
import os
import tempfile
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

# Load environment variables
load_dotenv()

# Use Streamlit secrets for API key
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
elif os.getenv("GOOGLE_API_KEY") is None:
    st.error("❌ GOOGLE_API_KEY not found. Please add it to .streamlit/secrets.toml")
    st.stop()

# Initialize model
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# Streamlit UI
st.set_page_config(page_title="Resume Parser", layout="wide")
st.title("📄 AI Resume Parser with LangChain + Google Gemini")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    text = ""

    try:
        if file_type == "pdf":
            # Save PDF temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
            text = "\n".join([doc.page_content for doc in docs])

        elif file_type == "docx":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            loader = Docx2txtLoader(tmp_path)
            docs = loader.load()
            text = "\n".join([doc.page_content for doc in docs])

        elif file_type == "txt":
            stringio = uploaded_file.getvalue().decode("utf-8")
            text = stringio

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    # Show extracted text
    st.subheader("📑 Extracted Text")
    st.text_area("Resume Content", text, height=250)

    # Parse Resume Button
    if st.button("🔍 Parse Resume"):
        with st.spinner("Parsing resume with AI..."):
            prompt = PromptTemplate(
                input_variables=["resume"],
                template="""
                Extract the following information from the resume text below:
                - Full Name
                - Email Address
                - Phone Number
                - Skills
                - Education
                - Work Experience

                Resume:
                {resume}
                """
            )

            final_prompt = prompt.format(resume=text)
            response = model.invoke(final_prompt)

            try:
                parsed_output = json.loads(response.content)
            except:
                parsed_output = {"parsed_text": response.content}

            st.success("✅ Resume Parsed Successfully")
            st.json(parsed_output)
