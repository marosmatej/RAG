"""
Ephemeral minimal RAG server that keeps no local data on disk.
- Upload documents (PDF/TXT/DOCX) -> processed in memory
- Query uses lightweight retrieval + Groq API for generation
- No persistence: everything is in RAM and cleared on process exit or via `/clear`

Environment:
- Set `GROQ_API_KEY` in environment or in `.env`.
"""
import os
import io
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# lightweight deps
import PyPDF2
from docx import Document as DocxDocument

# Load env explicitly from project root (so running from `backend/` still picks it up)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not set. Set it in environment or project .env before using Groq.")

# OpenAI-compatible client (created only if key present)
from openai import OpenAI

# local modules
from ephemeral_store import EphemeralStore

# chunking params
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

app = FastAPI(title="Ephemeral Minimal RAG", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

store = EphemeralStore()
client = None
if GROQ_API_KEY:
    try:
        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    except Exception as e:
        # keep client None and surface errors when generating
        print(f"Error creating Groq/OpenAI client: {e}")
# model selection (configurable via env)
GROQ_MODEL = os.getenv("GROQ_MODEL") or "gpt-4o-mini"

# Pydantic models
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


# helpers
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    cid = 0
    L = len(text)
    while start < L:
        end = start + chunk_size
        if end > L:
            end = L
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"text": chunk, "chunk_id": cid, "start_char": start, "end_char": end})
            cid += 1
        start = max(end - overlap, end)
        if start >= L:
            break
    return chunks


async def extract_text_from_upload(file: UploadFile) -> str:
    ext = Path(file.filename).suffix.lower()
    content = await file.read()
    if ext == ".pdf":
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            parts = []
            # iterate pages to avoid huge memory spikes
            for p in reader.pages:
                try:
                    t = p.extract_text()
                except Exception:
                    t = None
                if t:
                    parts.append(t)
            return "\n".join(parts)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF parse error: {e}")
    elif ext == ".txt":
        try:
            return content.decode("utf-8", errors="replace")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"TXT parse error: {e}")
    elif ext == ".docx":
        try:
            bio = io.BytesIO(content)
            doc = DocxDocument(bio)
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DOCX parse error: {e}")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported extension: {ext}")


@app.get("/")
async def root():
    return {"message": "Ephemeral Minimal RAG - no local data stored", "version": "1.0"}


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    # Process in-memory only
    filename = file.filename
    try:
        text = await extract_text_from_upload(file)
        chunks = chunk_text(text)
        store.add_documents(chunks, filename)
        print(f"[upload] Stored {len(chunks)} chunks for file: {filename}")
        return UploadResponse(status="success", filename=filename, chunks=len(chunks), message="Uploaded and indexed in-memory")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    q = request.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # retrieve
    hits = store.search(q, top_k=3)
    if not hits:
        return QueryResponse(answer="No documents indexed. Upload docs first.", sources=[])

    # prepare context
    context = "\n\n".join([f"[Source {i+1} from {h['metadata']['filename']}]:\n{h['text']}" for i, h in enumerate(hits)])
    prompt = f"You are a helpful assistant. Use the context to answer. Context:\n{context}\n\nQuestion: {q}\n\nAnswer concisely based only on the context."

    if client is None:
        raise HTTPException(status_code=500, detail="Groq/OpenAI client not configured. Set GROQ_API_KEY in .env or environment and restart the server.")

    try:
        resp = client.chat.completions.create(model=GROQ_MODEL, messages=[{"role":"user","content":prompt}], temperature=0.0, max_tokens=400)
        answer = resp.choices[0].message.content
    except Exception as e:
        answer = f"Generation error: {e}"

    sources = [{"filename": h["metadata"]["filename"], "chunk_id": h["metadata"]["chunk_id"], "text": (h["text"][:200]+"...") if len(h["text"])>200 else h["text"]} for h in hits]
    return QueryResponse(answer=answer, sources=sources)


@app.delete('/documents/{filename}')
async def delete_doc(filename: str):
    try:
        store.delete_document(filename)
        return {"message": f"Deleted {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_docs():
    return {"documents": store.list_documents(), "total": len(store.list_documents())}


@app.get('/stats')
async def stats():
    """Return simple stats and stored document names for debugging."""
    try:
        s = store.stats()
        return {"stats": s, "documents": store.list_documents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
async def clear():
    store.clear()
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_ephemeral:app", host="0.0.0.0", port=8000, reload=True)
