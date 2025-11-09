# Simple RAG System 📚

A minimalistic Retrieval-Augmented Generation (RAG) system with a clean web interface. Upload documents, ask questions, and get AI-generated answers based on your content.

## Features ✨

- 📤 Upload PDF, TXT, and DOCX documents
- 🔍 Semantic search using vector embeddings
- 🤖 AI-powered answers using LLM (Ollama or OpenAI)
- 💬 Clean and responsive web interface
- 📊 View and manage uploaded documents
- 🎯 Source citations for generated answers

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- LangChain (RAG orchestration)
- ChromaDB (Vector database)
- Sentence Transformers (Embeddings)
- Ollama or OpenAI (LLM)

**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- No frameworks - pure simplicity!

## Prerequisites 📋

1. **Python 3.9+** installed
2. **Ollama** (recommended for free local LLM) OR **OpenAI API key**

### Install Ollama (Recommended - Free & Local)

1. Download from [ollama.ai](https://ollama.ai)
2. Install and run: `ollama run llama2`
3. Verify it's running: `ollama list`

### OR Get OpenAI API Key

1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Note: Costs ~$0.002 per query

## Installation 🚀

### Step 1: Clone/Setup Project

```powershell
cd "c:\Users\marko\Documents\RAG"
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

This will install all required packages (may take a few minutes).

### Step 4: Configure Environment

Copy the example environment file:
```powershell
cd ..
copy .env.example .env
```

Edit `.env` file with your settings:

**For Ollama (Local - Recommended):**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**For OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_actual_api_key_here
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Running the Application 🎯

### Start Backend Server

```powershell
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Open Frontend

Open `frontend\index.html` in your web browser, or use a simple HTTP server:

```powershell
cd frontend
python -m http.server 8080
```

Then navigate to: `http://localhost:8080`

## Usage Guide 📖

### 1. Upload Documents

1. Click **"Choose File"** button
2. Select a PDF, TXT, or DOCX file
3. Click **"Upload"**
4. Wait for processing (documents are chunked and embedded)

### 2. Ask Questions

1. Type your question in the text area
2. Click **"Ask Question"** or press Enter
3. Wait for the AI to generate an answer
4. View the answer and source citations

### 3. Manage Documents

- Click **"Refresh"** to update the documents list
- Click **"Delete"** next to a document to remove it

## Example Questions 💡

Once you've uploaded documents, try questions like:

- "What is the main topic of this document?"
- "Summarize the key points."
- "What does the document say about [specific topic]?"
- "List the main conclusions."

## API Endpoints 🔌

The backend provides a REST API:

- `GET /` - API information
- `POST /upload` - Upload document
- `POST /query` - Ask question
- `GET /docs` - List documents
- `GET /stats` - Collection statistics
- `DELETE /docs/{filename}` - Delete document

API documentation: `http://localhost:8000/docs`

## Project Structure 📁

```
RAG/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── rag_pipeline.py         # RAG logic
│   ├── document_processor.py   # Document handling
│   ├── vector_store.py         # Vector DB operations
│   ├── config.py               # Configuration
│   └── requirements.txt        # Dependencies
│
├── frontend/
│   ├── index.html             # Main UI
│   ├── style.css              # Styling
│   └── app.js                 # Frontend logic
│
├── data/
│   ├── uploads/               # Uploaded documents
│   └── vector_db/             # Vector database
│
├── .env                       # Configuration (create from .env.example)
├── .env.example               # Example configuration
├── .gitignore                 # Git ignore rules
├── ARCHITECTURE.md            # System design
└── README.md                  # This file
```

## Troubleshooting 🔧

### Backend won't start

- **Error: Module not found**
  - Solution: Make sure virtual environment is activated and dependencies installed
  - Run: `pip install -r backend/requirements.txt`

- **Error: Address already in use**
  - Solution: Port 8000 is busy, change PORT in .env file

### Frontend can't connect

- **"Cannot connect to backend"**
  - Solution: Make sure backend is running on port 8000
  - Check: `http://localhost:8000` in browser

### Ollama errors

- **"Error connecting to Ollama"**
  - Solution: Make sure Ollama is running
  - Run: `ollama serve` or `ollama run llama2`
  - Check: `http://localhost:11434` should respond

### Upload errors

- **"Unsupported file format"**
  - Solution: Only PDF, TXT, DOCX are supported
  - Check file extension

- **File too large**
  - Solution: Increase MAX_UPLOAD_SIZE in .env
  - Default is 10MB

## Configuration Options ⚙️

Edit `.env` file to customize:

| Setting | Description | Default |
|---------|-------------|---------|
| `LLM_PROVIDER` | LLM to use (ollama/openai) | ollama |
| `OLLAMA_MODEL` | Ollama model name | llama2 |
| `OPENAI_API_KEY` | Your OpenAI API key | - |
| `CHUNK_SIZE` | Characters per chunk | 500 |
| `CHUNK_OVERLAP` | Overlap between chunks | 50 |
| `MAX_UPLOAD_SIZE` | Max file size (bytes) | 10485760 |

## Available Models 🤖

### Ollama Models (Free)
- `llama2` - Good general purpose (default)
- `mistral` - Fast and efficient
- `codellama` - For code documents
- `llama2:13b` - Larger, more accurate

Install: `ollama pull <model-name>`

### OpenAI Models (Paid)
- `gpt-3.5-turbo` - Fast and cheap
- `gpt-4` - Most accurate

## Tips for Best Results 💯

1. **Upload related documents** - The system works best when documents are about similar topics
2. **Ask specific questions** - More specific questions get better answers
3. **Check sources** - Always review the source citations
4. **Chunk size matters** - Smaller chunks (300-500) for specific info, larger (800-1000) for context
5. **Use good models** - Better LLMs = better answers (try llama2:13b or gpt-4)

## Development 👨‍💻

### Adding new document types

Edit `backend/document_processor.py` and add a new extraction method.

### Changing vector store

Edit `backend/vector_store.py` to implement FAISS or another vector DB.

### Customizing UI

Edit `frontend/style.css` for styling changes.

## Future Enhancements 🚀

- [ ] Streaming responses
- [ ] Chat history
- [ ] Multiple document queries
- [ ] Advanced chunking strategies
- [ ] Document preview
- [ ] Export conversations
- [ ] User authentication

## License 📄

This is a simple educational project. Feel free to use and modify as needed.

## Credits 🙏

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)
- [ChromaDB](https://www.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Ollama](https://ollama.ai/)

## Support 💬

Having issues? Check:
1. All dependencies installed: `pip list`
2. Backend running: `http://localhost:8000`
3. Ollama running: `http://localhost:11434`
4. Console errors in browser DevTools (F12)

---

**Happy RAG-ing! 🎉**
