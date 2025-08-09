from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import os
import aiofiles
import requests
import asyncio
import shutil

from document_ingestion import chunk_documents
from vector_store import VectorStore
from query_engine import QueryEngine
from llm_reasoner import generate_answer

# -------------------- FastAPI Setup --------------------
app = FastAPI(title="Hackathon RAG Document QA")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Paths --------------------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize components
vector_store = VectorStore(index_file="vector_index.faiss", meta_file="vector_metadata.pkl")
query_engine = QueryEngine(index_file="vector_index.faiss", meta_file="vector_metadata.pkl")

# -------------------- Routes --------------------
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Hackathon RAG Document QA API is running!",
        "endpoints": {
            "upload": "/upload/ (POST)",
            "query": "/query/ (POST)",
            "hackrx": "/hackrx/run (POST)"
        }
    }


@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload files, process them, and update the FAISS index."""
    if not files:
        return {"error": "No files uploaded."}

    # -------------------- Save Files Concurrently --------------------
    async def save_file(file: UploadFile) -> str:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)
        return file_path

    saved_files = await asyncio.gather(*(save_file(f) for f in files))

    # -------------------- Extract and Chunk Documents --------------------
    loop = asyncio.get_event_loop()
    chunks = await loop.run_in_executor(None, chunk_documents, saved_files)

    if not chunks:
        return {"message": "No text could be extracted from the uploaded files."}

    # -------------------- Update FAISS Index --------------------
    vector_store.build_index(chunks)
    vector_store.save_index()
    query_engine.vector_store.index = vector_store.index
    query_engine.vector_store.metadata = vector_store.metadata

    return {
        "message": f"Processed {len(saved_files)} files into {len(chunks)} chunks and updated FAISS index."
    }


@app.post("/query/")
async def query_documents(payload: Dict = Body(...)):
    """
    Query documents with one or multiple questions.
    Expected JSON:
    {
        "queries": ["Question 1", "Question 2"],
        "top_k": 5
    }
    """
    queries = payload.get("queries", [])
    top_k = payload.get("top_k", 5)

    if not queries:
        return {"error": "No queries provided."}

    if not query_engine.is_ready():
        return {"error": "FAISS index is not loaded. Upload documents first."}

    async def process_question(q: str):
        results = query_engine.query(query_text=q, top_k=top_k)
        # Offload LLM to thread to avoid blocking
        structured_answer = await asyncio.to_thread(generate_answer, q, results)
        return {"question": q, "results": structured_answer}

    answers = await asyncio.gather(*(process_question(q) for q in queries))
    return {"answers": answers}


@app.post("/hackrx/run")
async def hackrx_run(payload: Dict = Body(...)):
    """
    Endpoint for HackRx challenge.
    Expected JSON:
    {
        "documents": "https://example.com/file.pdf",
        "questions": ["Question 1", "Question 2"]
    }
    """
    documents_url = payload.get("documents")
    if isinstance(documents_url, list):
        documents_url = documents_url[0]

    questions = payload.get("questions", [])

    if not documents_url or not questions:
        return {"error": "Missing 'documents' URL or 'questions' list."}

    # -------------------- Download document --------------------
    doc_filename = os.path.join(UPLOAD_DIR, os.path.basename(documents_url.split("?")[0]))
    with requests.get(documents_url, stream=True) as r:
        with open(doc_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    # -------------------- Process and Index --------------------
    loop = asyncio.get_event_loop()
    chunks = await loop.run_in_executor(None, chunk_documents, [doc_filename])

    vector_store.build_index(chunks)
    vector_store.save_index()
    query_engine.vector_store.index = vector_store.index
    query_engine.vector_store.metadata = vector_store.metadata

    # -------------------- Answer Questions Concurrently --------------------
    async def process_question(q: str):
        results = query_engine.query(query_text=q, top_k=5)
        structured_answer = await asyncio.to_thread(generate_answer, q, results)
        return {"question": q, "results": structured_answer}

    answers = await asyncio.gather(*(process_question(q) for q in questions))
    return {"answers": answers}
