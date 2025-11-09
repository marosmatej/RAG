from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import shutil
import os
import sys
from typing import List, Dict

# Ensure prints show immediately
sys.stdout.flush()

print("=" * 60)
print("Starting RAG System Backend...")
print("=" * 60)
sys.stdout.flush()

print("\n[1/4] Importing configuration...")
from config import settings
print(f"✓ Configuration loaded. LLM Provider: {settings.llm_provider}")

print("\n[2/4] Importing document processor...")
from document_processor import DocumentProcessor
print("✓ Document processor imported")

print("\n[3/4] Importing vector store (this may take a while first time)...")
from vector_store import VectorStore
print("✓ Vector store imported")

print("\n[4/4] Importing RAG pipeline...")
from rag_pipeline import RAGPipeline
print("✓ RAG pipeline imported")

print("\n" + "=" * 60)
print("All modules imported successfully!")
print("=" * 60 + "\n")


# Initialize FastAPI app
print("Initializing FastAPI app...")
app = FastAPI(
    title="Simple RAG System",
    description="A minimalistic Retrieval-Augmented Generation system",
    version="1.0.0"
)
print("✓ FastAPI app created")

# Add CORS middleware to allow frontend requests
print("Adding CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("✓ CORS middleware added")

# Initialize components
print("\nInitializing components...")
print("  - Creating document processor...")
document_processor = DocumentProcessor(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)
print("  ✓ Document processor ready")

print("  - Creating vector store (downloading embedding model if first time)...")
print("    This may take 1-2 minutes on first run to download ~400MB model...")
vector_store = VectorStore(
    persist_directory=str(settings.vector_db_dir),
    embedding_model=settings.embedding_model
)
print("  ✓ Vector store ready")

print("  - Creating RAG pipeline...")
rag_pipeline = RAGPipeline(vector_store)
print("  ✓ RAG pipeline ready")

print("\n" + "=" * 60)
print("🚀 Backend initialization complete!")
print("=" * 60 + "\n")


# Pydantic models for request/response
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]


class UploadResponse(BaseModel):
    status: str
    filename: str
    chunks: int
    message: str


class DocumentListResponse(BaseModel):
    documents: List[str]
    total: int


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    documents: List[str]


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Simple RAG System API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "query": "/query",
            "documents": "/docs",
            "stats": "/stats"
        }
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document
    
    Args:
        file: Uploaded file (PDF, TXT, or DOCX)
        
    Returns:
        Upload status and metadata
    """
    # Validate file extension
    allowed_extensions = {'.pdf', '.txt', '.docx'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file
    file_path = settings.uploads_dir / file.filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Process document
    try:
        print(f"Processing document: {file.filename}")
        chunks = document_processor.process_document(file_path)
        print(f"Created {len(chunks)} chunks")
        
        # Add to vector store
        print("Adding to vector store...")
        vector_store.add_documents(chunks, file.filename)
        print("Successfully added to vector store")
        
        return UploadResponse(
            status="success",
            filename=file.filename,
            chunks=len(chunks),
            message=f"Document '{file.filename}' uploaded and processed successfully"
        )
    
    except Exception as e:
        # Clean up file if processing failed
        print(f"Error processing document: {str(e)}")
        import traceback
        traceback.print_exc()
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Ask a question about uploaded documents
    
    Args:
        request: Query request with question
        
    Returns:
        Generated answer with sources
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = rag_pipeline.generate_answer(request.question, top_k=3)
        return QueryResponse(
            answer=result['answer'],
            sources=result['sources']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@app.get("/docs", response_model=DocumentListResponse)
async def list_documents():
    """
    List all uploaded documents
    
    Returns:
        List of document filenames
    """
    try:
        documents = vector_store.list_documents()
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get collection statistics
    
    Returns:
        Statistics about documents and chunks
    """
    try:
        stats = vector_store.get_collection_stats()
        return StatsResponse(
            total_documents=stats['total_documents'],
            total_chunks=stats['total_chunks'],
            documents=stats['documents']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.delete("/docs/{filename}")
async def delete_document(filename: str):
    """
    Delete a document from the system
    
    Args:
        filename: Name of the document to delete
        
    Returns:
        Deletion status
    """
    try:
        # Delete from vector store
        vector_store.delete_document(filename)
        
        # Delete physical file
        file_path = settings.uploads_dir / filename
        if file_path.exists():
            file_path.unlink()
        
        return {"status": "success", "message": f"Document '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
