✅ Steps to Deploy the AI Resume Parser Online
1. Prepare the GitHub Repository

Include these files:

resume-parser/
├── app.py                # Main Streamlit app
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Ignore .env, pycache, logs
└── LICENSE               # Optional (MIT License)


Do NOT commit .env or .streamlit/secrets.toml.

2. Set Up Dependencies

Create requirements.txt:

streamlit
python-dotenv
langchain-openai
langchain-google-genai
langchain-community


Streamlit Cloud uses this file to install packages automatically.

3. Add API Key via Streamlit Secrets

In Streamlit Cloud:

Go to Settings → Secrets for your app.

Add your key:

GOOGLE_API_KEY = "your_google_api_key_here"


In app.py, read it with:

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

4. Push Repo to GitHub

Make sure all necessary files are committed.

Do not include .env or .streamlit/secrets.toml in the repo.

5. Deploy on Streamlit Cloud

Log in to Streamlit Cloud
.

Click “New app” → Connect GitHub repository.

Select branch and main file (app.py).

Streamlit Cloud automatically installs dependencies from requirements.txt.

Launch the app — your AI Resume Parser is now fully online.

6. Use the App Online

Open the app URL.

Upload a resume (PDF, DOCX, TXT).

Preview text.

Click “Parse with AI” to generate JSON.

View or download parsed JSON.

This workflow ensures:

Safe API key management (via secrets).

Correct dependencies (via requirements.txt).

Minimal errors with JSON parsing (regex fallback in app.py).

Fully online deployment without local setup.
