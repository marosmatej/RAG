// API Base URL - Change this if your backend runs on a different port
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const documentsList = document.getElementById('documentsList');
const refreshBtn = document.getElementById('refreshBtn');
const questionInput = document.getElementById('questionInput');
const queryBtn = document.getElementById('queryBtn');
const answerContainer = document.getElementById('answerContainer');
const answer = document.getElementById('answer');
const sourcesContainer = document.getElementById('sourcesContainer');
const sources = document.getElementById('sources');
const queryStatus = document.getElementById('queryStatus');

// Event Listeners
fileInput.addEventListener('change', handleFileSelect);
uploadBtn.addEventListener('click', handleUpload);
refreshBtn.addEventListener('click', loadDocuments);
queryBtn.addEventListener('click', handleQuery);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleQuery();
    }
});

// Initialize
loadDocuments();

// File Selection Handler
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = file.name;
        uploadBtn.disabled = false;
    } else {
        fileName.textContent = 'No file chosen';
        uploadBtn.disabled = true;
    }
}

// Upload Handler
async function handleUpload() {
    const file = fileInput.files[0];
    if (!file) return;

    // Disable button and show loading
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';
    showStatus(uploadStatus, 'Uploading document...', 'info');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const txt = await response.text();
        let data = null;
        try {
            data = JSON.parse(txt);
        } catch (e) {
            // non-JSON response
        }

        if (response.ok) {
            const msg = data ? `${data.message} (${data.chunks} chunks created)` : 'Uploaded';
            showStatus(uploadStatus, `✓ ${msg}`, 'success');
            
            // Reset form
            fileInput.value = '';
            fileName.textContent = 'No file chosen';
            
            // Reload documents list
            loadDocuments();
        } else {
            showStatus(uploadStatus, `✗ Error: ${data && data.detail ? data.detail : txt}`, 'error');
            uploadBtn.disabled = false;
        }
    } catch (error) {
        showStatus(uploadStatus, `✗ Error: ${error.message}`, 'error');
        uploadBtn.disabled = false;
    } finally {
        uploadBtn.textContent = 'Upload';
    }
}

// Load Documents
async function loadDocuments() {
    documentsList.innerHTML = '<p class="loading">Loading documents...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/documents`);
        const txt = await response.text();
        let data = null;
        try { data = JSON.parse(txt); } catch (e) { /* ignore */ }

        if (response.ok) {
            displayDocuments(data && data.documents ? data.documents : []);
        } else {
            documentsList.innerHTML = `<p class="error">Error loading documents: ${data && data.detail ? data.detail : escapeHtml(txt)}</p>`;
        }
    } catch (error) {
        documentsList.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Display Documents
function displayDocuments(docs) {
    if (docs.length === 0) {
        documentsList.innerHTML = '<p class="loading">No documents uploaded yet.</p>';
        return;
    }

    documentsList.innerHTML = docs.map(doc => `
        <div class="document-item">
            <span class="document-name">📄 ${doc}</span>
            <button class="btn btn-danger" onclick="deleteDocument('${doc}')">Delete</button>
        </div>
    `).join('');
}

// Delete Document
async function deleteDocument(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/documents/${encodeURIComponent(filename)}`, {
            method: 'DELETE'
        });

        const txt = await response.text();
        let data = null;
        try { data = JSON.parse(txt); } catch (e) { /* ignore */ }

        if (response.ok) {
            loadDocuments();
            showStatus(uploadStatus, `✓ ${data && data.message ? data.message : 'Deleted'}`, 'success');
        } else {
            showStatus(uploadStatus, `✗ Error: ${data && data.detail ? data.detail : escapeHtml(txt)}`, 'error');
        }
    } catch (error) {
        showStatus(uploadStatus, `✗ Error: ${error.message}`, 'error');
    }
}

// Query Handler
async function handleQuery() {
    const question = questionInput.value.trim();
    
    if (!question) {
        showStatus(queryStatus, 'Please enter a question.', 'error');
        return;
    }

    // Disable button and show loading
    queryBtn.disabled = true;
    queryBtn.textContent = 'Thinking...';
    answerContainer.classList.add('hidden');
    showStatus(queryStatus, 'Searching documents and generating answer...', 'info');

    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        const txt = await response.text();
        let data = null;
        try { data = JSON.parse(txt); } catch (e) { /* ignore */ }

        if (response.ok) {
            displayAnswer(data && data.answer ? data.answer : 'No answer returned', data && data.sources ? data.sources : []);
            hideStatus(queryStatus);
        } else {
            showStatus(queryStatus, `✗ Error: ${data && data.detail ? data.detail : escapeHtml(txt)}`, 'error');
        }
    } catch (error) {
        showStatus(queryStatus, `✗ Error: ${error.message}`, 'error');
    } finally {
        queryBtn.disabled = false;
        queryBtn.textContent = 'Ask Question';
    }
}

// Display Answer
function displayAnswer(answerText, sourcesData) {
    // Show answer
    answer.textContent = answerText;
    answerContainer.classList.remove('hidden');

    // Show sources if available
    if (sourcesData && sourcesData.length > 0) {
        sources.innerHTML = sourcesData.map((source, index) => `
            <div class="source-item">
                <div class="source-header">Source ${index + 1}: ${escapeHtml(source.filename || '')}</div>
                <div class="source-text">${escapeHtml(source.text || source.snippet || '')}</div>
            </div>
        `).join('');
        sourcesContainer.classList.remove('hidden');
    } else {
        sourcesContainer.classList.add('hidden');
    }
}

// Small helper to avoid injecting raw HTML from backend into the page
function escapeHtml(unsafe) {
    return String(unsafe)
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/\"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Status Message Helpers
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message show ${type}`;
}

function hideStatus(element) {
    element.className = 'status-message';
}

// Check Backend Connection on Load
async function checkBackend() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (!response.ok) {
            showStatus(uploadStatus, '⚠ Warning: Cannot connect to backend server. Make sure it is running.', 'error');
        }
    } catch (error) {
        showStatus(uploadStatus, '⚠ Warning: Cannot connect to backend server. Make sure it is running on port 8000.', 'error');
    }
}

// Check backend on page load
checkBackend();
