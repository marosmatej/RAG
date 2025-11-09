import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # LLM Configuration
    llm_provider: Literal["openai", "ollama", "groq"] = "groq"
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-70b-versatile"
    
    # Embedding Configuration
    embedding_provider: Literal["sentence-transformers", "openai"] = "sentence-transformers"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Vector Store Configuration
    vector_store: str = "chromadb"
    chroma_persist_directory: str = "../data/vector_db"
    
    # Document Processing
    max_upload_size: int = 10485760  # 10MB
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    uploads_dir: Path = base_dir / "data" / "uploads"
    vector_db_dir: Path = base_dir / "data" / "vector_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
