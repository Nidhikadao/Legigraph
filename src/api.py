"""
FastAPI Backend Application for LegiGraph: Legislative Policy Impact RAG.
Week 4 Implementation: Pydantic schemas, POST /query, POST /upload, GET /documents,
GET /health, error handling with HTTPException, and CORS.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import settings, DATA_DIR
from src.ingestion import extract_and_clean_pdf
from src.chunker import LegislativeChunker
from src.vectorstore import VectorStoreManager
from src.rag_chain import LegislativeRAGChain

# Initialize FastAPI App
app = FastAPI(
    title="LegiGraph API",
    description="Statutory Interpretation & Legislative Policy Impact RAG System",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared singletons
vstore_manager = VectorStoreManager()
rag_chain = LegislativeRAGChain(vector_store_manager=vstore_manager)
chunker = LegislativeChunker()


# --- Pydantic Schemas ---
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Legislative or policy impact question", example="What grant assistance is available for small businesses?")
    demographic: Optional[str] = Field("General Public", description="Target civic or demographic group", example="Small Business Owners")
    top_k: Optional[int] = Field(settings.SIMILARITY_TOP_K, ge=1, le=10, description="Number of source chunks to retrieve")

class SourceCitation(BaseModel):
    chunk_id: str
    source: str
    page_number: int
    section: str
    relevance_score: float
    snippet: str

class QueryResponse(BaseModel):
    query: str
    demographic: str
    answer: str
    sources: List[SourceCitation]
    total_sources_retrieved: int

class UploadResponse(BaseModel):
    filename: str
    pages_processed: int
    chunks_created: int
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    total_chunks_indexed: int
    embedding_model: str


# --- API Endpoints ---
@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Welcome to LegiGraph: Legislative Policy Impact RAG API",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Returns system status and vector database statistics."""
    try:
        stats = vstore_manager.get_stats()
        return HealthResponse(
            status="healthy",
            app=settings.APP_NAME,
            version=settings.APP_VERSION,
            total_chunks_indexed=stats["total_chunks_indexed"],
            embedding_model=stats["embedding_model"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database or embedding model service unavailable: {str(e)}"
        )

@app.get("/demographics", tags=["Policy"])
async def list_target_demographics():
    """Lists pre-configured demographic profiles for impact filtering."""
    return {"demographics": settings.TARGET_DEMOGRAPHICS}

@app.get("/documents", tags=["Documents"])
async def list_documents():
    """Lists ingested PDF documents in the data folder and chunk counts."""
    files = list(DATA_DIR.glob("*.pdf"))
    stats = vstore_manager.get_stats()
    return {
        "total_documents": len(files),
        "documents": [f.name for f in files],
        "total_chunks_indexed": stats["total_chunks_indexed"]
    }

@app.post("/query", response_model=QueryResponse, tags=["RAG Pipeline"])
async def query_legislative_rag(req: QueryRequest):
    """
    Executes the RAG pipeline:
    - Semantically searches ChromaDB for legislative sections
    - Generates grounded answers with demographic impact analysis
    - Returns source citations with exact page numbers
    """
    if not req.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty or blank."
        )
        
    try:
        result = rag_chain.query(
            question=req.query,
            demographic=req.demographic or "General Public",
            top_k=req.top_k or settings.SIMILARITY_TOP_K
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing RAG query: {str(e)}"
        )

@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_pdf_bill(
    file: UploadFile = File(..., description="Legislative bill in PDF format")
):
    """
    Uploads a new legislative PDF, cleans running headers/footers,
    splits into recursive chunks, and indexes them into ChromaDB in real-time.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported for legislative document ingestion."
        )
        
    saved_file_path = DATA_DIR / file.filename
    try:
        # Save file to disk
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Run extraction & regex cleaning
        pages = extract_and_clean_pdf(str(saved_file_path))
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="PDF could not be parsed or contains no readable text."
            )
            
        # Recursive Chunking
        chunks = chunker.chunk_document_pages(pages)
        
        # Batch upload to ChromaDB
        vstore_manager.batch_upload_chunks(chunks)
        
        return UploadResponse(
            filename=file.filename,
            pages_processed=len(pages),
            chunks_created=len(chunks),
            status="success",
            message=f"Successfully parsed, cleaned, chunked, and indexed '{file.filename}' into ChromaDB."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest PDF document: {str(e)}"
        )
