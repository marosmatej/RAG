import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid
import sys

# Add flush to ensure prints show immediately
def debug_print(msg):
    print(msg)
    sys.stdout.flush()


class VectorStore:
    """Manages vector embeddings and similarity search"""
    
    def __init__(self, persist_directory: str, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector store with ChromaDB
        
        Args:
            persist_directory: Directory to persist the vector database
            embedding_model: Name of the sentence transformer model
        """
        debug_print(f"    [VectorStore] Initializing with model: {embedding_model}")
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        debug_print(f"    [VectorStore] Setting up ChromaDB at: {persist_directory}")
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory)
            )
            debug_print(f"    [VectorStore] ChromaDB client ready")
        except Exception as e:
            debug_print(f"    [VectorStore] Error creating ChromaDB client: {e}")
            debug_print(f"    [VectorStore] Try deleting: {self.persist_directory}")
            raise
        
        # Initialize embedding model
        debug_print(f"    [VectorStore] Loading embedding model (this takes time on first run)...")
        debug_print(f"    [VectorStore] Downloading to: ~/.cache/huggingface/")
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            debug_print(f"    [VectorStore] Embedding model loaded!")
        except Exception as e:
            debug_print(f"    [VectorStore] Error loading embedding model: {e}")
            raise
        
        # Get or create collection
        debug_print(f"    [VectorStore] Getting/creating document collection...")
        try:
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            debug_print(f"    [VectorStore] Collection ready with {self.collection.count()} existing documents")
        except Exception as e:
            debug_print(f"    [VectorStore] Error creating collection: {e}")
            raise
    
    def add_documents(self, chunks: List[Dict[str, Any]], filename: str):
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of text chunks with metadata
            filename: Name of the source document
        """
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Create unique IDs for each chunk
        ids = [f"{filename}_{chunk['chunk_id']}" for chunk in chunks]
        
        # Prepare metadata
        metadatas = [
            {
                'filename': filename,
                'chunk_id': chunk['chunk_id'],
                'start_char': chunk['start_char'],
                'end_char': chunk['end_char']
            }
            for chunk in chunks
        ]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar chunks with metadata and scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def delete_document(self, filename: str):
        """
        Delete all chunks of a specific document
        
        Args:
            filename: Name of the document to delete
        """
        # Get all IDs for this document
        results = self.collection.get(
            where={"filename": filename}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
    
    def list_documents(self) -> List[str]:
        """
        List all unique documents in the vector store
        
        Returns:
            List of document filenames
        """
        # Get all documents
        results = self.collection.get()
        
        if not results['metadatas']:
            return []
        
        # Extract unique filenames
        filenames = set(meta['filename'] for meta in results['metadatas'])
        return sorted(list(filenames))
    
    def get_collection_stats(self) -> Dict[str, int]:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        documents = self.list_documents()
        
        return {
            'total_chunks': count,
            'total_documents': len(documents),
            'documents': documents
        }
