# RAG System Architecture

## Overview
A simple Retrieval-Augmented Generation (RAG) system with a minimalistic web interface.

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (UI)                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Simple HTML/CSS/JavaScript Interface                   │  │
│  │  • Document Upload Component                              │  │
│  │  • Question Input Field                                   │  │
│  │  • Answer Display Area                                    │  │
│  │  • Loading States & Error Handling                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI/Flask)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  API Endpoints:                                           │  │
│  │  • POST /upload - Upload and process documents           │  │
│  │  • POST /query  - Ask questions                          │  │
│  │  • GET  /docs   - List uploaded documents                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG Pipeline Components                     │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Document        │  │  Vector Store    │  │  LLM         │  │
│  │  Processing      │  │                  │  │  Integration │  │
│  │                  │  │  • ChromaDB      │  │              │  │
│  │  • Text Loader   │──▶  • FAISS         │◀─┤  • OpenAI    │  │
│  │  • Chunking      │  │  • Simple JSON   │  │  • Ollama    │  │
│  │  • Embeddings    │  │    Vector DB     │  │  • HuggingF. │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling (minimalistic design)
- **Vanilla JavaScript** - Interactivity (no framework needed)
- **Optional**: TailwindCSS for quick styling

### Backend
- **Python 3.9+**
- **FastAPI** - Fast, modern web framework
- **Uvicorn** - ASGI server

### RAG Components
- **LangChain** - RAG pipeline orchestration
- **Sentence Transformers** - Local embeddings (all-MiniLM-L6-v2)
- **ChromaDB** or **FAISS** - Vector storage
- **OpenAI API** or **Ollama** - LLM for generation

### Document Processing
- **PyPDF2** or **pdfplumber** - PDF processing
- **python-docx** - Word documents
- **tiktoken** - Token counting and chunking

## Data Flow

### 1. Document Upload Flow
```
User uploads document
    ↓
Backend receives file
    ↓
Extract text from document
    ↓
Split text into chunks (with overlap)
    ↓
Generate embeddings for each chunk
    ↓
Store embeddings in vector database
    ↓
Return success status to user
```

### 2. Query Flow
```
User asks question
    ↓
Generate embedding for question
    ↓
Search vector DB for similar chunks (top-k)
    ↓
Retrieve relevant document chunks
    ↓
Create prompt with context + question
    ↓
Send to LLM
    ↓
Return generated answer to user
```

## Project Structure

```
RAG/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── rag_pipeline.py         # RAG logic
│   ├── document_processor.py   # Document handling
│   ├── vector_store.py         # Vector DB operations
│   ├── config.py               # Configuration
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── index.html             # Main UI
│   ├── style.css              # Styling
│   └── app.js                 # Frontend logic
│
├── data/
│   ├── uploads/               # Uploaded documents
│   └── vector_db/             # Vector database storage
│
├── .env                       # Environment variables (API keys)
├── .gitignore
└── README.md                  # Setup instructions
```

## Key Features

### Core Features (MVP)
1. ✅ Upload PDF/TXT documents
2. ✅ Process and index documents
3. ✅ Ask questions about uploaded documents
4. ✅ Display answers with source references
5. ✅ View list of uploaded documents

### Optional Enhancements
- 🔄 Document deletion
- 🔄 Chat history
- 🔄 Multiple document types (DOCX, CSV, etc.)
- 🔄 Streaming responses
- 🔄 Citation highlighting
- 🔄 Advanced chunking strategies

## Configuration Options

### Embedding Models
- **Local**: `sentence-transformers/all-MiniLM-L6-v2` (free, fast)
- **OpenAI**: `text-embedding-ada-002` (paid, high quality)

### LLM Options
- **Ollama** (local, free): llama2, mistral, etc.
- **OpenAI** (paid): gpt-3.5-turbo, gpt-4
- **HuggingFace** (free tier available)

### Vector Store Options
- **ChromaDB**: Easy to use, persistent, embedded
- **FAISS**: Fast, in-memory (save to disk)
- **Simple JSON**: Custom implementation for learning

## Setup & Running

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
- Simply open `frontend/index.html` in browser
- Or use a simple HTTP server: `python -m http.server 8080`

## API Endpoints

### POST /upload
Upload and process a document
```json
Request: multipart/form-data with 'file'
Response: {
  "status": "success",
  "filename": "document.pdf",
  "chunks": 42
}
```

### POST /query
Ask a question
```json
Request: {
  "question": "What is the main topic?"
}
Response: {
  "answer": "The main topic is...",
  "sources": ["chunk1", "chunk2"]
}
```

### GET /docs
List all uploaded documents
```json
Response: {
  "documents": ["doc1.pdf", "doc2.txt"]
}
```

## Security Considerations
- Input validation for file uploads
- File size limits
- Sanitize user inputs
- Rate limiting for API calls
- Secure API key storage in .env

---

## Next Steps
1. Review this architecture
2. Choose LLM provider (Ollama for free, OpenAI for best quality)
3. Choose vector store (ChromaDB recommended)
4. Start implementation

Ready to proceed? Let me know if you want to adjust anything!
