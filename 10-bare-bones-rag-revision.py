from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
import streamlit as st

load_dotenv()
DATA_DIR = 'data/handbook'

Settings.llm = GoogleGenAI(model= "gemini-2.5-flash")
Settings.embed_model = HuggingFaceEmbedding(model_name= "BAAI/bge-small-en-v1.5")

# --- CORE LOGIC ---
@st.cache_resource
def get_query_engine():
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Gemini API Key is required.")
        str.stop()
    str.info("Loading documents and creating index")

    documents = SimpleDirectoryReader('data/handbook').load_data()
    index = VectorStoreIndex.from_documents(documents)
    str.success("RAG Index complete!")

    return index.as_query_engine()



# --- STREAMLIT UI ---
st.title("Bare Bones RAG Chatbot")
query_engine = get_query_engine()
prompt = st.chat_input("Ask me  a question...")


if prompt:
    st.write(f"User: {prompt}")
    response = query_engine.query(prompt)
    bot_response = response.response
    st.write(f"Chatbot response {bot_response}")