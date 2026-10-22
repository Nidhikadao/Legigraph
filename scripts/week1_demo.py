"""
Week 1 Milestone Demo Script:
Converts a 5-page legislative PDF into a list of cleaned, overlapping text chunks,
saves them to data/chunks.json, and prints them clearly in the terminal.
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings, DEFAULT_PDF_PATH, CHUNKS_JSON_PATH
from src.ingestion import extract_and_clean_pdf
from src.chunker import LegislativeChunker
from scripts.generate_sample_bill import create_sample_legislative_bill

def run_week1_demo():
    print("=" * 80)
    print("  LEGISGRAPH: WEEK 1 - PDF INGESTION & RECURSIVE CHUNKING PIPELINE")
    print("=" * 80)
    
    # 1. Ensure sample PDF exists
    pdf_path = DEFAULT_PDF_PATH
    if not pdf_path.exists():
        print(f"[*] Generating sample 5-page legislative PDF at {pdf_path}...")
        create_sample_legislative_bill(str(pdf_path))
    else:
        print(f"[+] Found legislative PDF: {pdf_path}")
        
    # 2. Extract and clean PDF with PyMuPDF and Regex cleaner
    print("\n--- STEP 1: PyMuPDF Extraction & Regex Cleaning ---")
    pages = extract_and_clean_pdf(str(pdf_path))
    print(f"Total Pages Processed: {len(pages)}")
    for p in pages:
        print(f"  • Page {p['page_number']}: Raw Chars = {p['raw_length']} -> Cleaned Chars = {p['cleaned_length']} | Sections Detected: {p['sections']}")
        
    # 3. Recursive Character Chunking
    print(f"\n--- STEP 2: Recursive Character Text Splitting (Size={settings.CHUNK_SIZE}, Overlap={settings.CHUNK_OVERLAP}) ---")
    chunker = LegislativeChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    chunks = chunker.chunk_document_pages(pages)
    
    print(f"Generated {len(chunks)} overlapping text chunks across {len(pages)} pages.")
    
    # 4. Save to JSON
    saved_path = chunker.save_chunks_to_json(chunks, CHUNKS_JSON_PATH)
    print(f"[+] Saved structured chunks to: {saved_path}")
    
    # 5. Terminal output display for developer verification
    print("\n--- STEP 3: Terminal Output of Cleaned, Overlapping Chunks ---")
    for i, chunk in enumerate(chunks, 1):
        print("\n" + "-" * 70)
        print(f"CHUNK #{i:02d} | ID: {chunk['chunk_id']} | Page: {chunk['page_number']} | Section: {chunk['section']}")
        print(f"Chars: {chunk['char_count']} | Words: {chunk['word_count']}")
        print("-" * 70)
        print(chunk['content'])
        
    print("\n" + "=" * 80)
    print(" WEEK 1 MILESTONE SUCCESS: Verified 5-page PDF -> Cleaned Overlapping Chunks")
    print("=" * 80)
    return chunks

if __name__ == "__main__":
    run_week1_demo()
