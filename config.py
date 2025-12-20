import os

# ===== GROQ API KEY FROM ENV =====
# Streamlit secrets or system env will fill this
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ===== APP SETTINGS =====
APP_NAME = "HR Analytics Assistant V3"
DEFAULT_LANGUAGE = "en"
