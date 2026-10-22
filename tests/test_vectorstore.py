"""
Unit tests for ChromaDB Vector Store and Semantic Search.
"""

from src.vectorstore import VectorStoreManager
from src.chunker import LegislativeChunker
from src.ingestion import extract_and_clean_pdf
from src.config import DEFAULT_PDF_PATH

def test_vectorstore_upload_and_search(tmp_path):
    test_db_dir = tmp_path / "test_db"
    vstore = VectorStoreManager(persist_dir=str(test_db_dir), collection_name="test_bills")
    
    pages = extract_and_clean_pdf(str(DEFAULT_PDF_PATH))
    chunker = LegislativeChunker()
    chunks = chunker.chunk_document_pages(pages)
    
    # Upload chunks
    uploaded = vstore.batch_upload_chunks(chunks)
    assert uploaded == len(chunks)
    
    # Query test
    results = vstore.similarity_search("small business grants", top_k=2)
    assert len(results) == 2
    assert "content" in results[0]
    assert "page_number" in results[0]
    assert "relevance_score" in results[0]
