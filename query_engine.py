from vector_store import VectorStore
from typing import List, Dict

class QueryEngine:
    def __init__(self, index_file="vector_index.faiss", meta_file="vector_metadata.pkl"):
        self.vector_store = VectorStore(index_file=index_file, meta_file=meta_file)
        try:
            self.vector_store.load_index()
        except FileNotFoundError:
            print("[INFO] No existing FAISS index loaded. Upload documents first.")

    def is_ready(self) -> bool:
        return self.vector_store.index is not None

    def query(self, query_text: str, top_k: int = 5) -> List[Dict]:
        return self.vector_store.search(query_text, top_k=top_k)
