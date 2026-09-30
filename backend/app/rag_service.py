import pypdf
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class RAGService:
    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        reader = pypdf.PdfReader(pdf_path)
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        return extracted_text

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def process_and_index_pdf(self, pdf_path: str) -> int:
        text = self.extract_text_from_pdf(pdf_path)
        if not text.strip():
            raise ValueError("No extractable text found in PDF.")
        
        raw_chunks = self.chunk_text(text)
        embeddings = self.embedder.encode(raw_chunks, show_progress_bar=False)
        
        # Reset current index and chunks for single document session
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(embeddings, dtype=np.float32))
        self.chunks = raw_chunks
        
        return len(raw_chunks)

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        if not self.chunks or self.index.ntotal == 0:
            return ""
        
        query_vector = self.embedder.encode([query])
        distances, indices = self.index.search(np.array(query_vector, dtype=np.float32), top_k)
        
        retrieved_texts = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                retrieved_texts.append(self.chunks[idx])
                
        return "\n\n---\n\n".join(retrieved_texts)