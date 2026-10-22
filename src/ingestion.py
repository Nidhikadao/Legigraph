"""
PDF Ingestion and Legislative Text Cleaning Pipeline.
Week 1 Implementation: PyMuPDF extraction, regex cleaning for legislative bills.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf  # PyMuPDF

class LegislativeTextCleaner:
    """Cleans raw PDF text from legislative bills using regular expressions."""
    
    # Common legislative headers (e.g. 118TH CONGRESS, H.R. 4082, CONGRESSIONAL RECORD)
    HEADER_PATTERNS = [
        re.compile(r'^\s*\d{1,3}(?:ST|ND|RD|TH)\s+CONGRESS.*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^\s*H\.R\.\s*\d+.*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^\s*S\.\s*\d+.*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^\s*CONGRESSIONAL RECORD\b.*$', re.IGNORECASE | re.MULTILINE),
    ]
    
    # Common footers and page numbering
    FOOTER_PATTERNS = [
        re.compile(r'^\s*Page\s+\d+\s+(?:of|\/)\s+\d+.*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^\s*-\s*\d+\s*-\s*$', re.MULTILINE),
        re.compile(r'^\s*\[Page\s+\d+\]\s*$', re.IGNORECASE | re.MULTILINE),
    ]
    
    # Standalone line numbers typical of legislative bills (e.g. margin numbers 1-25)
    LINE_NUMBER_PATTERN = re.compile(r'^\s*([1-9]|[12][0-9])\s+(?=[A-Za-z(])', re.MULTILINE)
    STANDALONE_NUMBER = re.compile(r'^\s*\d{1,3}\s*$', re.MULTILINE)
    
    # Multiple whitespace and repeated empty lines
    MULTIPLE_SPACES = re.compile(r'[ \t]+')
    MULTIPLE_NEWLINES = re.compile(r'\n{3,}')
    
    @classmethod
    def clean(cls, raw_text: str) -> str:
        """
        Cleans raw extracted text:
        - Removes running headers
        - Removes running footers & page numbers
        - Strips legislative margin line numbers
        - Normalizes spaces and newlines
        """
        if not raw_text:
            return ""
            
        cleaned = raw_text
        
        # Remove headers
        for pattern in cls.HEADER_PATTERNS:
            cleaned = pattern.sub('', cleaned)
            
        # Remove footers
        for pattern in cls.FOOTER_PATTERNS:
            cleaned = pattern.sub('', cleaned)
            
        # Remove legislative line numbers
        cleaned = cls.LINE_NUMBER_PATTERN.sub('', cleaned)
        cleaned = cls.STANDALONE_NUMBER.sub('', cleaned)
        
        # Clean up bullet/delimiter lines like "• 2D SESSION •"
        cleaned = re.sub(r'•\s*[^•\n]+\s*•', '', cleaned)
        
        # Normalize whitespace per line
        lines = [cls.MULTIPLE_SPACES.sub(' ', line).strip() for line in cleaned.splitlines()]
        
        # Reconstruct with clean newlines
        cleaned = '\n'.join(line for line in lines if line)
        cleaned = cls.MULTIPLE_NEWLINES.sub('\n\n', cleaned)
        
        return cleaned.strip()


class PDFDocumentLoader:
    """Loads and extracts text and metadata from PDF files using PyMuPDF (fitz)."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {self.file_path}")
            
    def load(self) -> List[Dict[str, Any]]:
        """
        Opens PDF with PyMuPDF, extracts text per page, applies regex cleaning,
        and attaches metadata.
        Returns a list of page dicts.
        """
        doc = pymupdf.open(str(self.file_path))
        pages_data = []
        
        bill_filename = self.file_path.name
        total_pages = len(doc)
        
        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1
            raw_text = page.get_text("text")
            
            cleaned_text = LegislativeTextCleaner.clean(raw_text)
            
            # Detect section titles in page
            section_matches = re.findall(r'(SECTION\s+\d+[\.\:][^\n]+)', cleaned_text, re.IGNORECASE)
            
            pages_data.append({
                "page_number": page_num,
                "total_pages": total_pages,
                "source": bill_filename,
                "file_path": str(self.file_path),
                "raw_length": len(raw_text),
                "cleaned_length": len(cleaned_text),
                "sections": section_matches,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text
            })
            
        doc.close()
        return pages_data


def extract_and_clean_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Convenience helper to load and clean a PDF."""
    loader = PDFDocumentLoader(file_path)
    return loader.load()
