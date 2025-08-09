import pickle
from typing import List, Dict
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class VectorStore:
    def __init__(self, index_file="vector_index.faiss", meta_file="vector_metadata.pkl"):
        self.index_file = index_file
        self.meta_file = meta_file
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.metadata = []

    def build_index(self, chunks: List[Dict]):
        """Build FAISS index with batched embeddings."""
        texts = [c["text"] for c in chunks]
        embeddings = self.model.encode(texts, batch_size=16, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")

        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])

        self.index.add(embeddings)
        self.metadata.extend(chunks)

    def save_index(self):
        """Save FAISS index and metadata."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, "wb") as f:
            pickle.dump(self.metadata, f)

    def load_index(self):
        """Load FAISS index and metadata."""
        if not os.path.exists(self.index_file) or not os.path.exists(self.meta_file):
            raise FileNotFoundError("No existing FAISS index or metadata found.")

        self.index = faiss.read_index(self.index_file)
        with open(self.meta_file, "rb") as f:
            self.metadata = pickle.load(f)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search top_k similar chunks for a query."""
        if self.index is None:
            raise RuntimeError("Index not loaded.")

        query_vec = np.array([self.model.encode(query)], dtype="float32")
        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.metadata[idx])
        return results
