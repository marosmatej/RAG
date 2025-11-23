"""
In-memory ephemeral store for uploaded document chunks.
No persistence to disk — data lives only while the process runs.
"""
from typing import List, Dict, Any


class EphemeralStore:
    """Simple in-memory store for document chunks."""

    def __init__(self):
        self.documents: Dict[str, List[Dict[str, Any]]] = {}

    def add_documents(self, chunks: List[Dict[str, Any]], filename: str):
        """Store chunks in memory under filename."""
        self.documents[filename] = chunks

    def search(self, query: str, top_k: int = 3):
        """Very lightweight keyword/substr scoring search."""
        if not self.documents:
            return []

        q = query.lower()
        q_words = set(q.split())

        scored = []
        for fname, chunks in self.documents.items():
            for chunk in chunks:
                text = chunk.get("text", "")
                t = text.lower()
                score = 0
                # substring match gets strong boost
                if q in t:
                    score += 10
                # word overlap
                score += len(q_words & set(t.split()))
                if score > 0:
                    scored.append({
                        "text": text,
                        "metadata": {"filename": fname, "chunk_id": chunk.get("chunk_id", 0)},
                        "score": score,
                    })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def list_documents(self):
        return list(self.documents.keys())

    def delete_document(self, filename: str):
        if filename in self.documents:
            del self.documents[filename]

    def clear(self):
        self.documents.clear()

    def stats(self):
        total_chunks = sum(len(chunks) for chunks in self.documents.values())
        return {"total_documents": len(self.documents), "total_chunks": total_chunks}
