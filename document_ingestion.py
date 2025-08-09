import os
from typing import List, Dict
import fitz  # PyMuPDF
import docx
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] PDF extraction failed for {pdf_path}: {e}")
    return text.strip()

def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from DOCX files."""
    try:
        doc = docx.Document(docx_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        print(f"[ERROR] DOCX extraction failed for {docx_path}: {e}")
        return ""

def extract_text_from_txt(txt_path: str) -> str:
    """Extract text from TXT files."""
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"[ERROR] TXT extraction failed for {txt_path}: {e}")
        return ""

def clean_text(text: str) -> str:
    """Remove extra spaces and line breaks."""
    return re.sub(r'\s+', ' ', text).strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

def chunk_documents(file_paths: List[str]) -> List[Dict]:
    """Extract, clean, and chunk all supported documents."""
    chunks_metadata = []
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        if ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif ext == ".docx":
            text = extract_text_from_docx(file_path)
        elif ext == ".txt":
            text = extract_text_from_txt(file_path)
        else:
            print(f"[WARNING] Unsupported file type: {file_path}")
            continue

        text = clean_text(text)
        if not text:
            continue

        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            chunks_metadata.append({
                "text": chunk,
                "source": os.path.basename(file_path),
                "page": i + 1
            })
    return chunks_metadata
