import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.prompts import Prompt
import json

# Load environment variables (for local development)
load_dotenv()

# Get API key from Streamlit secrets if available, else fallback to .env
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

if not GOOGLE_API_KEY:
    st.error("❌ Google API key is missing. Please add it to .streamlit/secrets.toml or .env")
    st.stop()

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)

# Streamlit UI
st.title("📄 Resume Parser App")
st.write("Upload a resume and extract structured information using LangChain + Google Generative AI")

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])

if uploaded_file:
    file_type = uploaded_file.type
    file_path = f"temp_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Load file
    if file_type == "application/pdf":
        loader = PyPDFLoader(file_path)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        loader = Docx2txtLoader(file_path)
    else:
        loader = TextLoader(file_path)

    documents = loader.load()
    text_content = " ".join([doc.page_content for doc in documents])

    st.subheader("📌 Extracted Text Preview")
    st.text_area("Content", text_content[:1000] + "...", height=200)

    # Define parsing prompt
    prompt_template = """
    Extract the following details from the resume:
    - Name
    - Email
    - Phone Number
    - Skills
    - Education
    - Work Experience

    Return the output in JSON format.
    Resume text: {resume}
    """
    prompt = Prompt(template=prompt_template, input_variables=["resume"])

    response = llm.predict(prompt.format(resume=text_content))

    try:
        parsed_data = json.loads(response)
        st.subheader("✅ Extracted Resume Information")
        st.json(parsed_data)
    except:
        st.error("⚠️ Failed to parse structured JSON output. Showing raw response instead:")
        st.write(response)
