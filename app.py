import os
import json
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key)

# Prompt for parsing resume
template = """
You are a professional resume parser.
Extract the following details in JSON format:
- Name
- Email
- Phone
- Skills
- Education
- Experience

Resume Content:
{resume_text}
"""

prompt = PromptTemplate(input_variables=["resume_text"], template=template)
chain = LLMChain(llm=llm, prompt=prompt)

# Streamlit UI
st.title("📄 Resume Parser with Gemini")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Load resume content
    if uploaded_file.type == "application/pdf":
        loader = PyPDFLoader(uploaded_file)
        pages = loader.load()
        resume_text = " ".join([p.page_content for p in pages])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        loader = Docx2txtLoader(uploaded_file)
        resume_text = loader.load()[0].page_content
    else:
        loader = TextLoader(uploaded_file)
        resume_text = loader.load()[0].page_content

    st.write("✅ Resume uploaded successfully")

    if st.button("Parse Resume"):
        with st.spinner("Extracting details... ⏳"):
            response = chain.run(resume_text=resume_text)

            try:
                parsed_json = json.loads(response)
                st.json(parsed_json)   # Pretty JSON output
            except:
                st.write("⚠️ Could not parse JSON, showing raw response:")
                st.write(response)
