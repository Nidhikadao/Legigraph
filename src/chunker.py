"""
Text Splitting and Chunking Module.
Week 1 Implementation: LangChain RecursiveCharacterTextSplitter (chunk size 1000, overlap 200).
Saves segmented chunks to JSON for verification.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import settings, CHUNKS_JSON_PATH

class LegislativeChunker:
    """Segments cleaned legislative text into structured chunks preserving metadata."""
    
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\nSECTION ",
                "\nSec. ",
                "\n\n",
                "\n",
                ". ",
                "; ",
                " ",
                ""
            ],
            keep_separator=True
        )
        
    def chunk_document_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes cleaned page dictionaries from ingestion and splits them into chunks
        while tracking section context and source page numbers.
        """
        all_chunks = []
        global_chunk_idx = 0
        current_section = "General / Preamble"
        
        for page_data in pages:
            page_num = page_data["page_number"]
            source = page_data["source"]
            cleaned_text = page_data["cleaned_text"]
            
            if not cleaned_text:
                continue
                
            # Check if this page introduces new sections
            page_sections = page_data.get("sections", [])
            if page_sections:
                current_section = page_sections[0]
                
            # Split page text using LangChain's RecursiveCharacterTextSplitter
            splits = self.splitter.split_text(cleaned_text)
            
            for split_idx, split_text in enumerate(splits):
                # Check if split itself has a new section header
                section_match = re.search(r'(SECTION\s+\d+[\.\:][^\n]+)', split_text, re.IGNORECASE)
                if section_match:
                    current_section = section_match.group(1).strip()
                    
                chunk_id = f"{source}#p{page_num}#c{global_chunk_idx+1:03d}"
                
                chunk_obj = {
                    "chunk_id": chunk_id,
                    "source": source,
                    "page_number": page_num,
                    "section": current_section,
                    "chunk_index": global_chunk_idx,
                    "page_chunk_index": split_idx,
                    "char_count": len(split_text),
                    "word_count": len(split_text.split()),
                    "content": split_text
                }
                
                all_chunks.append(chunk_obj)
                global_chunk_idx += 1
                
        return all_chunks

    def save_chunks_to_json(self, chunks: List[Dict[str, Any]], output_path: Optional[Path] = None) -> str:
        """Saves chunks to a JSON file for inspection and verification."""
        path = output_path or CHUNKS_JSON_PATH
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "total_chunks": len(chunks),
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "chunks": chunks
            }, f, indent=2, ensure_ascii=False)
            
        return str(path)

    @staticmethod
    def load_chunks_from_json(json_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Loads chunks from JSON file."""
        path = json_path or CHUNKS_JSON_PATH
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("chunks", [])
