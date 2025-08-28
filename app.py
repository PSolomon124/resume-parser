# app.py

# -----------------------
# Installation (local only, not needed in Streamlit Cloud)
# pip install langchain_openai langchain-google-genai python-dotenv streamlit
# pip install -U langchain-community
# -----------------------

import os
import json
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

# -----------------------
# Step 1: Config / API Key
# -----------------------
load_dotenv()  # loads .env locally (ignored in deployment)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ No Google API Key found. Please set it in .env (local) or in Streamlit Cloud → Settings → Secrets.")
    st.stop()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY
)

# -----------------------
# Step 2: Prompt Template
# -----------------------
PROMPT_TEMPLATE = """
You are an expert resume parser. Given the resume text, extract the following fields and return a single valid JSON object:

{{
  "Name": "...",
  "Email": "...",
  "Phone": "...",
  "LinkedIn": "...",
  "Skills": [...],
  "Education": [...],
  "Experience": [...],
  "Projects": [...],
  "Certifications": [...],
  "Languages": [...]
}}

Rules:
- If a field cannot be found, set its value to "No idea".
- Return ONLY valid JSON (no extra commentary).
- Keep lists as arrays, and keep Experience/Projects as arrays of short strings.

Resume text:
{text}
"""

prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["text"])

# -----------------------
# Step 3: Resume Loader
# -----------------------
def load_resume_docs(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        temp_path = tmp_file.name

    if uploaded_file.name.endswith(".pdf"):
        loader = PyPDFLoader(temp_path)
    elif uploaded_file.name.endswith(".docx"):
        loader = Docx2txtLoader(temp_path)
    elif uploaded_file.name.endswith(".txt"):
        loader = TextLoader(temp_path)
    else:
        return None
    return loader.load()

# -----------------------
# Step 4: Streamlit UI
# -----------------------
def main():
    st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="centered")
    st.title("📄 Resume Parser — AI Powered")

    uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])

    if uploaded_file:
        with st.spinner("📂 Reading resume..."):
            docs = load_resume_docs(uploaded_file)
            if not docs:
                st.error("❌ Unsupported file type.")
                return

        st.subheader("📑 Extracted Text (Preview)")
        preview_text = "\n\n".join([d.page_content for d in docs])[:4000]
        st.text_area("Preview", value=preview_text, height=200)

        if st.button("🤖 Parse with AI"):
            with st.spinner("⏳ Parsing resume with LLM..."):
                full_text = "\n\n".join([d.page_content for d in docs])
                formatted_prompt = prompt.format(text=full_text)

                response = llm.invoke(formatted_prompt)

                try:
                    parsed_json = json.loads(response.content)
                    st.subheader("✅ Parsed Resume Data")
                    st.json(parsed_json)

                    # Download button for JSON
                    st.download_button(
                        "📥 Download JSON",
                        data=json.dumps(parsed_json, indent=2),
                        file_name="parsed_resume.json",
                        mime="application/json"
                    )

                except json.JSONDecodeError:
                    st.error("⚠️ Failed to parse JSON. Showing raw output:")
                    st.write(response.content)

if __name__ == "__main__":
    main()
