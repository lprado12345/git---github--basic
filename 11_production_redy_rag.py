import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env
load_dotenv()
# -----------------------------
# Configuration Validation
# -----------------------------
def require_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing API key. Add GEMINI_API_KEY=your_key to your .env file. "
            "Do NOT commit your .env file to GitHub."
        )
    return api_key


def require_data_directory(data_dir: str = "data") -> Path:
    path = Path(data_dir)
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Data directory not found: {path.resolve()}")

    files = [f for f in path.rglob("*") if f.is_file()]
    if len(files) == 0:
        raise FileNotFoundError(f"No files found inside data directory: {path.resolve()}")

    return path
# -----------------------------
# Cached Data Loader
# -----------------------------
@st.cache_data(show_spinner="Loading documents...")
def load_documents(data_dir: str = "data") -> list[str]:
    path = Path(data_dir)
    documents = []

    for file in path.rglob("*.txt"):
        documents.append(file.read_text(encoding="utf-8", errors="ignore"))

    return documents
# -----------------------------
# Startup Validation (Fast Fail)
# -----------------------------
try:
    API_KEY = require_api_key()
    DATA_DIR = require_data_directory("data")
    docs = load_documents("data")

except Exception as e:
    st.error("Application failed to start. Please check API key and data folder.")
    st.exception(e)
    st.stop()
    try:
        response = query_engine.query(user_input)
        st.write(response)

    except Exception as e:
        st.error("Query failed. Please try again.")
        st.exception(e)
