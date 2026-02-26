import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI


# -------------------------------
# CONFIGURATION VALIDATION
# -------------------------------

def validate_config():
    load_dotenv()

    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ Missing GOOGLE_API_KEY in .env file or environment variables.")
        st.stop()

    # Check data directory
    data_path = Path("data/handbook")
    if not data_path.exists():
        st.error("❌ Data directory 'data/handbook' does not exist.")
        st.stop()

    # Check files in directory
    files = list(data_path.glob("*"))
    if len(files) == 0:
        st.error("❌ No files found inside 'data/handbook'.")
        st.stop()

    return data_path


# -------------------------------
# CACHE RAG ENGINE
# -------------------------------

@st.cache_resource
def build_query_engine(data_path):
    try:
        Settings.llm = GoogleGenAI(model="gemini-2.5-flash")
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

        documents = SimpleDirectoryReader(str(data_path)).load_data()
        index = VectorStoreIndex.from_documents(documents)

        return index.as_query_engine()

    except Exception as e:
        st.error(f"❌ Failed to build RAG engine: {e}")
        st.stop()


# -------------------------------
# STREAMLIT UI
# -------------------------------

st.title("Production Ready RAG Chatbot")

data_path = validate_config()
query_engine = build_query_engine(data_path)

prompt = st.chat_input("Ask a question...")

if prompt:
    st.write(f"**You:** {prompt}")

    try:
        response = query_engine.query(prompt)
        st.write(f"**Bot:** {response}")

    except Exception as e:
        st.error(f"❌ Query failed: {e}")
