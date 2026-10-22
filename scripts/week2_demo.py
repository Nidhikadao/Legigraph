"""
Week 2 Milestone Demo Script:
Initializes ChromaDB in ./db, loads chunks from Week 1, batch uploads them with all-MiniLM-L6-v2 embeddings,
runs similarity searches for specific policy keywords, and asserts that retrieved chunks match policy topics.
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings, CHUNKS_JSON_PATH
from src.chunker import LegislativeChunker
from src.vectorstore import VectorStoreManager
from scripts.week1_demo import run_week1_demo

def run_week2_demo():
    print("=" * 80)
    print("  LEGISGRAPH: WEEK 2 - CHROMADB PERSISTENT STORAGE & EMBEDDINGS RETRIEVAL")
    print("=" * 80)
    
    # 1. Ensure chunks from Week 1 exist
    if not CHUNKS_JSON_PATH.exists():
        print("[*] Chunks JSON not found. Running Week 1 pipeline first...")
        chunks = run_week1_demo()
    else:
        chunks = LegislativeChunker.load_chunks_from_json(CHUNKS_JSON_PATH)
        print(f"[+] Loaded {len(chunks)} chunks from {CHUNKS_JSON_PATH}")
        
    # 2. Initialize ChromaDB Vector Store with sentence-transformers/all-MiniLM-L6-v2
    print(f"\n--- STEP 1: Connecting to ChromaDB at '{settings.CHROMA_PERSIST_DIR}' ---")
    vstore = VectorStoreManager()
    
    # Reset collection to avoid duplicate accumulation for demo reproducibility
    vstore.clear()
    
    # 3. Batch upload chunks with unique IDs
    print("\n--- STEP 2: Batch Uploading Chunks into Collection ---")
    uploaded_count = vstore.batch_upload_chunks(chunks)
    print(f"Indexed Chunks: {uploaded_count}")
    stats = vstore.get_stats()
    print(f"Collection Stats: {stats}")
    
    # 4. Test Queries for Policy Keywords
    test_queries = [
        {
            "query": "What grants are available for small business clean energy transition?",
            "expected_keyword": "$75,000",
            "topic": "Small Business Micro-Grants"
        },
        {
            "query": "What wage guarantees or stipends are given to displaced energy workers?",
            "expected_keyword": "$2,400",
            "topic": "Displaced Worker Transition Stipends"
        },
        {
            "query": "How will utility bills be capped for low income residential households?",
            "expected_keyword": "5 percent",
            "topic": "Low-Income Energy Bill Cap"
        }
    ]
    
    print("\n--- STEP 3: Executing Top-4 Similarity Searches ---")
    for t_idx, item in enumerate(test_queries, 1):
        q = item["query"]
        expected = item["expected_keyword"]
        topic = item["topic"]
        
        print("\n" + "=" * 70)
        print(f"QUERY #{t_idx} [{topic}]:")
        print(f"  \"{q}\"")
        print("=" * 70)
        
        results = vstore.similarity_search(query=q, top_k=4)
        print(f"Retrieved {len(results)} snippets from ChromaDB:")
        
        found_expected = False
        for rank, res in enumerate(results, 1):
            has_kw = expected.lower() in res["content"].lower()
            if has_kw:
                found_expected = True
            kw_flag = " [*** KEYWORD MATCH! ***]" if has_kw else ""
            
            print(f"\n  [Rank {rank}] Score: {res['relevance_score']:.4f} | Source: {res['source']} (Page {res['page_number']}) | Section: {res['section']}{kw_flag}")
            preview = res['content'].replace('\n', ' ')
            if len(preview) > 180:
                preview = preview[:180] + "..."
            print(f"         Snippet: \"{preview}\"")
            
        # Assertion check for retrieval quality
        assert found_expected, f"Failed assertion: Expected keyword '{expected}' not found in top-4 results for query '{q}'"
        print(f"\n  >>> PASS: Top-4 retrieval contains required policy keyword '{expected}'.")
        
    print("\n" + "=" * 80)
    print(" WEEK 2 MILESTONE SUCCESS: Top-4 Semantic Retrieval from ChromaDB Verified!")
    print("=" * 80)
    return vstore

if __name__ == "__main__":
    run_week2_demo()
