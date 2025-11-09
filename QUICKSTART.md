# Quick Start Guide 🚀

## Get Your RAG System Running in 5 Minutes!

### Step 1: Install Ollama (Free LLM)

1. Download from: https://ollama.ai/download
2. Install and run:
   ```powershell
   ollama run llama2
   ```
   Wait for it to download (~4GB), then it will start.

### Step 2: Set Up Python Environment

Open PowerShell in your RAG folder:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get an error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

This takes 2-3 minutes. Grab a coffee! ☕

### Step 4: Start the Backend

```powershell
python main.py
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

### Step 5: Open the Frontend

Open a new PowerShell window:

```powershell
cd frontend
python -m http.server 8080
```

Then open your browser to: http://localhost:8080

## That's It! 🎉

You can now:
1. Upload a document (PDF, TXT, or DOCX)
2. Ask questions about it
3. Get AI-generated answers with sources!

## Quick Test

1. Create a simple text file with some content
2. Upload it through the web interface
3. Ask: "What is this document about?"
4. See the magic happen! ✨

## Troubleshooting

**Problem: "Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`

**Problem: Import errors**
- Make sure venv is activated (you should see `(venv)` in your prompt)
- Reinstall: `pip install -r requirements.txt`

**Problem: Frontend can't connect**
- Backend must be running on port 8000
- Check: http://localhost:8000 in browser

## Need Help?

Check the full [README.md](README.md) for detailed documentation.

---

**Happy RAG-ing! 🚀**
