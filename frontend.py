import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Hackathon RAG Document QA", page_icon="📄", layout="wide")

st.title("📄 Hackathon RAG Document QA")
st.caption("Upload PDF, DOCX, or Email files, process them, and ask questions using LLM-powered retrieval.")

# -------------------- Upload --------------------
st.header("1️⃣ Upload and Process Documents")
uploaded_files = st.file_uploader("Upload PDF, DOCX, or Email files", type=["pdf", "docx", "eml"], accept_multiple_files=True)

if st.button("Process Documents", type="primary"):
    if not uploaded_files:
        st.error("Please upload at least one document.")
    else:
        files_data = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
        with st.spinner("Processing documents and updating FAISS index..."):
            response = requests.post(f"{API_URL}/upload/", files=files_data)
        if response.status_code == 200:
            st.success(response.json().get("message", "Documents processed successfully."))
        else:
            st.error("Failed to process documents. Check backend logs.")
            st.write(response.text)

st.divider()

# -------------------- Query --------------------
st.header("2️⃣ Ask Questions")
query_text = st.text_input("Enter your question", placeholder="e.g., What is the penalty for early contract termination?")
top_k = st.slider("Number of clauses to retrieve", 3, 10, 5)

if st.button("Get Answer"):
    if not query_text.strip():
        st.error("Please enter a question.")
    else:
        payload = {"queries": [query_text], "top_k": top_k}
        with st.spinner("Querying documents..."):
            response = requests.post(f"{API_URL}/query/", json=payload)
        if response.status_code == 200:
            answers = response.json().get("answers", [])
            for ans in answers:
                st.subheader(f"Question: {ans['question']}")
                st.json(ans["results"])
        else:
            st.error("Query failed. Check backend logs.")
            st.write(response.text)

st.divider()

# -------------------- HackRx Demo --------------------
st.header("3️⃣ HackRx API Demo")
doc_url = st.text_input("Document URL (PDF, DOCX, or Email)")
questions_input = st.text_area("Enter your questions (one per line)")

if st.button("Run HackRx Demo"):
    if not doc_url.strip() or not questions_input.strip():
        st.error("Please provide a document URL and at least one question.")
    else:
        questions = [q.strip() for q in questions_input.split("\n") if q.strip()]
        payload = {"documents": doc_url, "questions": questions}

        with st.spinner("Processing via HackRx endpoint..."):
            response = requests.post(f"{API_URL}/hackrx/run", json=payload)

        if response.status_code == 200:
            answers = response.json().get("answers", [])
            for ans in answers:
                st.subheader(f"Question: {ans['question']}")
                st.json(ans["results"])
        else:
            st.error("HackRx request failed. Check backend logs.")
            st.write(response.text)
