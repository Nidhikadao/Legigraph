"""
Unit tests for PDF Ingestion and Regex Text Cleaner.
"""

import os
from pathlib import Path
import pytest
from src.ingestion import LegislativeTextCleaner, PDFDocumentLoader
from src.config import DEFAULT_PDF_PATH
from scripts.generate_sample_bill import create_sample_legislative_bill

def test_regex_cleaning():
    raw_sample = """
    118TH CONGRESS • 2D SESSION • H.R. 4082
    Page 1 of 5 • CONGRESSIONAL RECORD
    1 SECTION 1. SHORT TITLE.
    2 This Act may be cited as the Clean Energy Act.
    Page 1 of 5
    """
    cleaned = LegislativeTextCleaner.clean(raw_sample)
    
    # Assert headers & footers removed
    assert "118TH CONGRESS" not in cleaned
    assert "CONGRESSIONAL RECORD" not in cleaned
    assert "Page 1 of 5" not in cleaned
    
    # Assert substantive legislative text preserved
    assert "SECTION 1. SHORT TITLE." in cleaned
    assert "Clean Energy Act" in cleaned

def test_pdf_document_loader():
    if not DEFAULT_PDF_PATH.exists():
        create_sample_legislative_bill(str(DEFAULT_PDF_PATH))
        
    loader = PDFDocumentLoader(str(DEFAULT_PDF_PATH))
    pages = loader.load()
    
    assert len(pages) == 5
    assert pages[0]["page_number"] == 1
    assert pages[0]["cleaned_length"] > 0
    assert pages[0]["cleaned_length"] < pages[0]["raw_length"]  # Cleaning reduced noise
    assert len(pages[0]["sections"]) > 0
