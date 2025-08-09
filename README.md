# 📄 AskMyDocs

An **LLM-powered Retrieval-Augmented Generation (RAG)** system that allows you to **upload documents (PDF, DOCX, TXT)**, process them into chunks, store them in a **FAISS vector database**, and query them using **OpenAI GPT models**.  
Also includes a **HackRx demo endpoint** for automated ingestion from document URLs.

---

## 🚀 Features
- **Document Upload** – PDF, DOCX, TXT file support.
- **Automatic Text Extraction & Cleaning**.
- **Chunking & Overlap** for better retrieval.
- **FAISS Vector Search** for semantic similarity.
- **LLM Reasoning** via OpenAI API.
- **Multiple Endpoints** for document upload, query, and HackRx demo.
- **Streamlit Frontend** for easy interaction.

---

## 📂 Project Structure
```
.
├── app.py                  # FastAPI backend
├── document_ingestion.py   # Document extraction, cleaning, and chunking
├── vector_store.py         # FAISS-based vector store management
├── query_engine.py         # Query handling using vector search
├── llm_reasoner.py         # LLM-powered answer generation
├── frontend.py             # Streamlit frontend
├── Pipfile                 # Pipenv dependency file
├── uploads/                # Uploaded documents storage
└── README.md               # Project documentation
```

---

## 🛠 Installation & Setup (Using Pipenv)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/hackathon-rag-qa.git
cd hackathon-rag-qa
```

### 2️⃣ Install Dependencies with Pipenv
```bash
pip install pipenv
pipenv install
```

Your `Pipfile` will include:
```toml
[packages]
fastapi = "*"
uvicorn = "*"
aiofiles = "*"
requests = "*"
python-docx = "*"
PyMuPDF = "*"
faiss-cpu = "*"
sentence-transformers = "*"
numpy = "*"
openai = "*"
streamlit = "*"
```

### 3️⃣ Activate the Virtual Environment
```bash
pipenv shell
```

### 4️⃣ Set Environment Variables
Create a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
```
Or set it directly in your shell:
```bash
export OPENAI_API_KEY="your_openai_api_key"   # macOS/Linux
set OPENAI_API_KEY="your_openai_api_key"      # Windows CMD
```

---

## ▶️ Running the Backend
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## 💻 Running the Frontend
```bash
streamlit run frontend.py
```

---

## 📌 API Usage

### **1. Upload Documents**
**POST** `/upload/`  
**Body (multipart/form-data)**:
```
files: [PDF/DOCX/TXT files]
```
**Response:**
```json
{
    "message": "Processed 2 files into 15 chunks and updated FAISS index."
}
```

---

### **2. Query Documents**
**POST** `/query/`  
**Body (JSON)**:
```json
{
    "queries": ["What is the penalty for early contract termination?"],
    "top_k": 5
}
```
**Response:**
```json
{
    "answers": [
        {
            "question": "What is the penalty for early contract termination?",
            "results": {
                "answer": "The penalty is 2 months' fees...",
                "docs_used": 3
            }
        }
    ]
}
```

---

### **3. HackRx Demo**
**POST** `/hackrx/run`  
**Body (JSON)**:
```json
{
    "documents": "https://example.com/file.pdf",
    "questions": ["Question 1", "Question 2"]
}
```
**Response:**
```json
{
    "answers": [
        {
            "question": "Question 1",
            "results": {
                "answer": "Answer text...",
                "docs_used": 2
            }
        }
    ]
}
```

---

## 📜 Document Processing Flow
1. **Upload** → Stored in `/uploads`.
2. **Extract Text** → Uses `PyMuPDF` for PDFs, `python-docx` for DOCX, plain read for TXT.
3. **Clean Text** → Removes extra spaces/line breaks.
4. **Chunking** → 500 words per chunk, 50-word overlap.
5. **Embed** → SentenceTransformer (`all-MiniLM-L6-v2`).
6. **Store** → FAISS vector index + metadata pickle.
7. **Query** → Semantic search → LLM reasoning.

---

## ⚠️ Notes
- Ensure **OpenAI API Key** is set before running.
- **Index files** (`vector_index.faiss` and `vector_metadata.pkl`) are generated automatically after first upload.
- Supports **PDF, DOCX, TXT** for now (can be extended).

---

## 📌 Future Improvements
- Support for **email (.eml)** ingestion.
- Add **multi-user session handling**.
- Use **async embedding** for faster processing.
- Deploy with **Docker**.

---

## 📄 License
MIT License © 2025 Your Name
