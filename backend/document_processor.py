import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import PyPDF2
from docx import Document


class DocumentProcessor:
    """Handles document loading and text extraction"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_document(self, file_path: Path) -> str:
        """
        Load and extract text from a document
        
        Args:
            file_path: Path to the document
            
        Returns:
            Extracted text content
        """
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self._extract_pdf(file_path)
        elif extension == '.txt':
            return self._extract_txt(file_path)
        elif extension == '.docx':
            return self._extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text_parts = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                print(f"Processing PDF with {num_pages} pages...")
                
                # Limit pages if too many
                max_pages = 500
                if num_pages > max_pages:
                    print(f"Warning: PDF has {num_pages} pages. Processing first {max_pages} pages only.")
                    num_pages = max_pages
                
                for i, page in enumerate(pdf_reader.pages[:num_pages]):
                    if i % 50 == 0 and i > 0:
                        print(f"Processed {i} pages...")
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {i}: {e}")
                        continue
                        
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
        
        return "\n".join(text_parts)
    
    def _extract_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Handle empty text
        if not text or len(text.strip()) == 0:
            return []
        
        # Simple character-based chunking
        chunks = []
        start = 0
        text_length = len(text)
        chunk_id = 0
        
        # Limit processing if text is too large
        max_text_length = 1_000_000  # 1 million characters max
        if text_length > max_text_length:
            print(f"Warning: Text is very large ({text_length} chars). Truncating to {max_text_length} chars.")
            text = text[:max_text_length]
            text_length = max_text_length
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Don't go beyond text length
            if end > text_length:
                end = text_length
            
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary (only if not at end)
            if end < text_length and len(chunk_text) > 50:
                # Look for sentence endings
                for delimiter in ['. ', '.\n', '! ', '?\n']:
                    last_delimiter = chunk_text.rfind(delimiter)
                    if last_delimiter != -1 and last_delimiter > len(chunk_text) * 0.5:
                        end = start + last_delimiter + len(delimiter)
                        chunk_text = text[start:end]
                        break
            
            # Only add non-empty chunks
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text.strip(),
                    'chunk_id': chunk_id,
                    'start_char': start,
                    'end_char': end
                })
                chunk_id += 1
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            
            # Prevent infinite loop
            if start >= text_length:
                break
        
        return chunks
    
    def process_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Complete pipeline: load document and chunk it
        
        Args:
            file_path: Path to document
            
        Returns:
            List of text chunks with metadata
        """
        text = self.load_document(file_path)
        chunks = self.chunk_text(text)
        
        # Add filename to metadata
        for chunk in chunks:
            chunk['filename'] = file_path.name
        
        return chunks
