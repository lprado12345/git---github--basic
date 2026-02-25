import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI


DATA_DIR = Path(__file__).parent / "data"


def setup_and_validate() -> tuple[bool, str]:
    """
    Returns (ok, message). Shows clear instructions if anything is missing.
    """
    # 1) Make sure data folder exists (create it if missing)
    DATA_DIR.mkdir(exist_ok=True)

    # 2) Load .env (from same folder as app.py)
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            False,
            "❌ GEMINI_API_KEY not found.\n\n"
            "Fix:\n"
            "1) Create a file named `.env` in the SAME folder as app.py\n"
            "2) Put this inside (no quotes):\n"
            "   GEMINI_API_KEY=PASTE_YOUR_KEY_HERE\n"
            "3) Restart: streamlit run app.py\n",
        )

    # google-genai tool reads from env
    os.environ["GEMINI_API_KEY"] = api_key

    # 3) Check for a PDF in /data
    pdfs = sorted([p for p in DATA_DIR.iterdir() if p.suffix.lower() == ".pdf"])
    if not pdfs:
        return (
            False,
            "❌ No PDF found in the `data` folder.\n\n"
            "Fix:\n"
            f"1) Put the Babson handbook PDF into this folder:\n   {DATA_DIR}\n"
            "2) Make sure it ends with .pdf\n"
            "3) Refresh the Streamlit page.\n",
        )

    if len(pdfs) > 1:
        names = "\n".join([f"- {p.name}" for p in pdfs])
        return (
            False,
            "❌ More than one PDF found in `data`.\n\n"
            "Fix: keep ONLY the Babson handbook PDF in `data`.\n\n"
            f"Currently found:\n{names}\n",
        )

    return True, f"✅ Setup OK.\nUsing PDF: {pdfs[0].name}\nData folder: {DATA_DIR}"


@st.cache_resource
def build_query_engine():
    # Settings: force Gemini (no OpenAI)
    Settings.llm = GoogleGenAI(model="gemini-2.5-flash")
    Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001")

    docs = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(docs)
    return index.as_query_engine(similarity_top_k=4)


def main():
    st.title("Activity 10 — Babson Handbook RAG Chatbot (Gemini + LlamaIndex)")

    ok, msg = setup_and_validate()
    with st.expander("✅ Setup / Debug Info", expanded=True):
        st.text(msg)
        st.text(f"Working directory: {Path.cwd()}")
        st.text(f"app.py location: {Path(__file__).parent}")

    if not ok:
        st.stop()

    qe = build_query_engine()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    user_q = st.chat_input("Ask a question about the Babson student handbook...")
    if user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.write(user_q)

        with st.chat_message("assistant"):
            with st.spinner("Searching handbook..."):
                answer = str(qe.query(user_q))
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

    st.divider()
    st.subheader("Required test questions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test: Transfer credit?"):
            q = "Can I get credit for courses taken somewhere else?"
            st.session_state.messages.append({"role": "user", "content": q})
            st.session_state.messages.append({"role": "assistant", "content": str(qe.query(q))})
            st.rerun()
    with col2:
        if st.button("Test: Interest-free loans?"):
            q = "Are any interest free loans offered?"
            st.session_state.messages.append({"role": "user", "content": q})
            st.session_state.messages.append({"role": "assistant", "content": str(qe.query(q))})
            st.rerun()


if __name__ == "__main__":
    main()