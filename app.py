# installation
# pip install langchain_openai langchain-google-genai python-dotenv streamlit
# pip install -U langchain-community

import os
import json
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.prompts import PromptTemplate

# -----------------------
# Step 1: Load API Key
# -----------------------
# First try Streamlit secrets, fallback to .env for local dev
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found. Please set it in `.streamlit/secrets.toml` (for deploy) or `.env` (for local).")
    st.stop()

# -----------------------
# Step 2: Config / LLM
# -----------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=api_key
)

PROMPT_TEMPLATE = """
You are an expert resume parser. Given the resume text, extract the following fields and return a single valid JSON object:

{
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
}

Rules:
- If a field cannot be found, set its value to "No idea".
- Return ONLY valid JSON (no extra commentary).
- Keep lists as arrays, and keep Experience/Projects as arrays of short strings.

Resume text:
{text}
"""

prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["text"])

# -----------------------
# Step 3: Helpers
# -----------------------
def load_resume_docs(uploaded_file):
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

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
    st.title("📄 Resume Parser — LangChain + Gemini")

    uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])

    if uploaded_file:
        with st.spinner("📥 Loading resume..."):
            docs = load_resume_docs(uploaded_file)
            if not docs:
                st.error("❌ Unsupported file type.")
                return

        st.subheader("📝 Extracted Text (Preview)")
        preview_text = "\n\n".join([d.page_content for d in docs])[:4000]
        st.text_area("Preview", value=preview_text, height=200)

        if st.button("🚀 Parse Resume"):
            with st.spinner("🤖 Extracting structured data..."):
                full_text = "\n\n".join([d.page_content for d in docs])
                formatted_prompt = prompt.format(text=full_text)

                response = llm.invoke(formatted_prompt)
                try:
                    parsed_json = json.loads(response.content)
                    st.success("✅ Resume Parsed Successfully!")
                    st.json(parsed_json)

                    # Download button
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(parsed_json, indent=2),
                        file_name="resume_parsed.json",
                        mime="application/json"
                    )
                except json.JSONDecodeError:
                    st.error("⚠️ Failed to parse JSON. Showing raw output instead.")
                    st.write(response.content)

if __name__ == "__main__":
    main()
