"""
Week 4 Milestone Test Script:
Uses FastAPI TestClient to verify /health, /documents, /query, and /upload endpoints.
Asserts proper status codes, JSON response structure, and source citations.
"""

import sys
import os
from pathlib import Path
from starlette.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.api import app
from src.config import DEFAULT_PDF_PATH

client = TestClient(app)

def run_api_tests():
    print("=" * 80)
    print("  LEGISGRAPH: WEEK 4 - FASTAPI ENDPOINTS & PIPELINE INTEGRATION TESTS")
    print("=" * 80)
    
    # 1. Test GET /health
    print("\n--- Test 1: GET /health ---")
    res_health = client.get("/health")
    print(f"Status: {res_health.status_code}")
    print(f"Payload: {res_health.json()}")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
    print(">>> PASS: Health endpoint returned 200 OK.")

    # 2. Test GET /documents
    print("\n--- Test 2: GET /documents ---")
    res_docs = client.get("/documents")
    print(f"Status: {res_docs.status_code}")
    print(f"Payload: {res_docs.json()}")
    assert res_docs.status_code == 200
    print(">>> PASS: Documents endpoint returned 200 OK.")

    # 3. Test POST /query (Demographic: Small Business Owners)
    print("\n--- Test 3: POST /query (Small Business Impact) ---")
    query_payload = {
        "query": "What are the clean energy transition grants for small businesses with under 40 employees?",
        "demographic": "Small Business Owners",
        "top_k": 3
    }
    res_query = client.post("/query", json=query_payload)
    print(f"Status: {res_query.status_code}")
    data = res_query.json()
    print(f"Query: {data['query']}")
    print(f"Demographic: {data['demographic']}")
    print(f"Total Sources: {data['total_sources_retrieved']}")
    print(f"Answer Preview:\n{data['answer'][:250]}...")
    
    assert res_query.status_code == 200
    assert len(data["sources"]) > 0
    assert "page_number" in data["sources"][0]
    print(">>> PASS: POST /query returned 200 OK with structured answer and source citations.")

    # 4. Test POST /upload (Upload PDF Bill)
    print("\n--- Test 4: POST /upload (PDF Bill Ingestion) ---")
    if not DEFAULT_PDF_PATH.exists():
        from scripts.generate_sample_bill import create_sample_legislative_bill
        create_sample_legislative_bill(str(DEFAULT_PDF_PATH))
        
    with open(DEFAULT_PDF_PATH, "rb") as f:
        files = {"file": (DEFAULT_PDF_PATH.name, f, "application/pdf")}
        res_upload = client.post("/upload", files=files)
        
    print(f"Status: {res_upload.status_code}")
    print(f"Payload: {res_upload.json()}")
    assert res_upload.status_code == 200
    assert res_upload.json()["status"] == "success"
    print(">>> PASS: POST /upload successfully ingested and indexed PDF.")

    # 5. Test Error Handling (Invalid file type)
    print("\n--- Test 5: Error Handling - Bad Request (Non-PDF Upload) ---")
    dummy_files = {"file": ("test.txt", b"plain text content", "text/plain")}
    res_err = client.post("/upload", files=dummy_files)
    print(f"Status: {res_err.status_code} (Expected 400)")
    assert res_err.status_code == 400
    print(">>> PASS: Error handling correctly rejected non-PDF upload.")

    print("\n" + "=" * 80)
    print(" WEEK 4 MILESTONE SUCCESS: All FastAPI Endpoints & Integration Tests Passed!")
    print("=" * 80)

if __name__ == "__main__":
    run_api_tests()
