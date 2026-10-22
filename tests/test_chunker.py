"""
Unit tests for RecursiveCharacterTextSplitter and chunk preservation.
"""

from src.ingestion import extract_and_clean_pdf
from src.chunker import LegislativeChunker
from src.config import DEFAULT_PDF_PATH
from scripts.generate_sample_bill import create_sample_legislative_bill

def test_chunking_and_metadata():
    if not DEFAULT_PDF_PATH.exists():
        create_sample_legislative_bill(str(DEFAULT_PDF_PATH))
        
    pages = extract_and_clean_pdf(str(DEFAULT_PDF_PATH))
    chunker = LegislativeChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.chunk_document_pages(pages)
    
    assert len(chunks) > 0
    first_chunk = chunks[0]
    assert "chunk_id" in first_chunk
    assert "page_number" in first_chunk
    assert "section" in first_chunk
    assert "content" in first_chunk
    assert first_chunk["char_count"] <= 1000 + 50  # Boundary check

def test_json_export_and_import(tmp_path):
    test_json_file = tmp_path / "test_chunks.json"
    chunker = LegislativeChunker()
    sample_chunks = [{
        "chunk_id": "test#p1#c001",
        "source": "bill.pdf",
        "page_number": 1,
        "section": "SECTION 1",
        "content": "Test text"
    }]
    
    saved = chunker.save_chunks_to_json(sample_chunks, output_path=test_json_file)
    loaded = chunker.load_chunks_from_json(json_path=test_json_file)
    
    assert len(loaded) == 1
    assert loaded[0]["chunk_id"] == "test#p1#c001"
