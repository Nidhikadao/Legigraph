"""
Configuration and settings for LegiGraph.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Default File Paths
DEFAULT_PDF_PATH = DATA_DIR / "sample_bill_clean_energy.pdf"
CHUNKS_JSON_PATH = DATA_DIR / "chunks.json"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App Settings
    APP_NAME: str = "LegiGraph: Legislative Policy Impact RAG"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Text Splitter Settings (Week 1 Spec: 1000 chunk size, 200 overlap)
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # ChromaDB & Embeddings (Week 2 Spec: sentence-transformers/all-MiniLM-L6-v2, ./db)
    CHROMA_PERSIST_DIR: str = str(DB_DIR)
    COLLECTION_NAME: str = "legislative_bills"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    SIMILARITY_TOP_K: int = 4
    
    # LLM Settings (Week 3 Spec: OpenAI, Gemini, Ollama, or Mock fallback)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")  # 'openai', 'gemini', 'ollama', or 'auto'
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL_NAME: str = os.getenv("OLLAMA_MODEL_NAME", "llama3.2")
    
    # Demographics for impact filtering
    TARGET_DEMOGRAPHICS: list[str] = [
        "Small Business Owners",
        "Rural Residents & Farmers",
        "Displaced Energy Workers",
        "Low-Income Households",
        "Senior Citizens (55+)",
        "Municipalities & Local Governments",
        "General Public"
    ]

settings = Settings()
