"""
Script to generate a beautifully formatted Word Document (.docx)
from the LegiGraph Interview & Project Guide.
"""

import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets inner padding for a table cell in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout(doc, text, title="KEY TAKEAWAY", border_color="10B981", bg_color="F0FDF4"):
    """Adds a stylish callout box."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_title = p.add_run(f"📌 {title}: ")
    run_title.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = RGBColor(16, 120, 80)
    
    run_text = p.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(10.5)
    run_text.font.color.rgb = RGBColor(30, 41, 59)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_docx(output_path: str):
    doc = Document()
    
    # Page setup - Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(51, 65, 85) # Slate 700
    
    # Title
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    run_title = title_p.add_run("⚖️ LegiGraph: Complete Project Architecture & Interview Guide")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42) # Slate 900
    
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(14)
    run_sub = sub_p.add_run("Demographic-Targeted Statutory Interpretation & Source-Audited Policy Impact Engine")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(100, 116, 139) # Slate 500
    
    # Divider line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(12)
    r_div = p_div.add_run("―" * 58)
    r_div.font.color.rgb = RGBColor(226, 232, 240)
    
    # Section 1: Executive Summary
    h1 = doc.add_heading("1. Executive Summary & Elevator Pitch", level=1)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)
    
    add_callout(
        doc,
        "LegiGraph translates dense congressional bills into plain-English, demographic-specific impacts (such as for small businesses, rural farmers, or seniors) with 100% verifiable statutory citations. Built in Python using PyMuPDF, LangChain, ChromaDB, HuggingFace embeddings, FastAPI, and Streamlit.",
        title="30-SECOND ELEVATOR PITCH",
        border_color="2563EB",
        bg_color="EFF6FF"
    )
    
    doc.add_heading("The 2-Minute In-Depth Interview Pitch", level=2)
    p = doc.add_paragraph(
        "\"Most RAG demos fall apart on legal documents because bills have recurring margin line numbers, running headers like '118th Congress', and complex cross-references that poison vector embeddings. Additionally, citizens don't read bills to understand statutory jargon; they want to know: 'How does this bill change my taxes, grants, or healthcare costs?'\n\n"
        "To solve this, I designed LegiGraph with five intentional engineering choices:\n"
        "1. A deterministic pre-processing stage that strips pagination and margin numbers while preserving statutory section hierarchies.\n"
        "2. Recursive character text splitting with legal delimiters (SECTION, Sec.) to maintain complete legal clauses.\n"
        "3. Metadata preservation tracking exact page numbers, section headers, and file origins for every chunk.\n"
        "4. A demographic-targeted RAG prompt with strict hallucination guardrails that replies 'I don't know' if an answer isn't grounded in the retrieved text.\n"
        "5. Dual delivery via a production-ready FastAPI backend with OpenAPI schemas and an Umbrel-inspired Streamlit dashboard with live document telemetry.\n\n"
        "The result is a transparent system where every generated insight links directly to verifiable page and section numbers with relevance scores.\""
    )
    p.paragraph_format.space_after = Pt(10)
    
    # Section 2: Why Naive RAG Fails
    h2 = doc.add_heading("2. The Core Problem: Why Traditional Search & Naive RAG Fail", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    
    # Comparison Table
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    hdr_cells = table.rows[0].cells
    headers = ["Dimension", "Naive Search / Generic RAG", "LegiGraph Approach"]
    widths = [Inches(1.5), Inches(2.5), Inches(2.5)]
    
    for i, h in enumerate(headers):
        hdr_cells[i].width = widths[i]
        set_cell_background(hdr_cells[i], "1E293B")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(10)
        
    data = [
        ("Document Noise", "Extracts headers, footers, and line numbers (1-25 on margins), corrupting semantic embeddings.", "Regex-based statutory cleaner strips congressional noise while keeping legal headings intact."),
        ("Chunking Logic", "Fixed token count (e.g. 500 tokens) cuts sentences, statutory rights, or penalty clauses in half.", "Recursive splitting prioritizing section boundaries (SECTION 3, Sec. 4(a))."),
        ("Query Perspective", "Generic summary: 'This bill addresses clean energy.'", "Demographic framing: 'For small businesses with under 40 employees, Section 3 provides $75,000 grants.'"),
        ("Hallucination Risk", "Model guesses or assumes facts when information is missing from the bill.", "Strict negative constraint: triggers explicit fallback if cosine relevance drops or topic is unmentioned."),
        ("Auditability", "Returns only text answers with no audit trail.", "Every response returns source filename, section title, page number, and similarity score.")
    ]
    
    for row_idx, (dim, naive, legi) in enumerate(data):
        row = table.add_row()
        bg = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, text in enumerate([dim, naive, legi]):
            c = row.cells[col_idx]
            c.width = widths[col_idx]
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if col_idx == 0:
                r.bold = True
                
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # Section 3: Technology Stack
    h3 = doc.add_heading("3. Technology Stack & Architectural Rationale", level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)
    
    tech_table = doc.add_table(rows=1, cols=3)
    tech_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_table.autofit = False
    
    t_hdr = tech_table.rows[0].cells
    for i, h in enumerate(["Layer", "Technology", "Why This Tech Was Chosen"]):
        t_hdr[i].width = widths[i]
        set_cell_background(t_hdr[i], "1E293B")
        set_cell_margins(t_hdr[i], top=100, bottom=100, left=120, right=120)
        p = t_hdr[i].paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(10)
        
    tech_data = [
        ("Language", "Python 3.10+ / 3.12", "Industry standard for AI/ML, NLP, and modern async web frameworks."),
        ("PDF Extraction", "PyMuPDF (fitz)", "Up to 10x faster than PyPDF2 or pdfplumber with exact text bounding and page-by-page metadata."),
        ("Text Chunking", "LangChain Text Splitters", "RecursiveCharacterTextSplitter allows custom regex separators to respect legal document morphology."),
        ("Vector DB", "ChromaDB (Persistent)", "Lightweight, serverless, zero-infrastructure local vector database with embedded SQLite/DuckDB. No external latency."),
        ("Embeddings", "sentence-transformers/all-MiniLM-L6-v2", "384-dimensional dense embeddings; fast CPU inference (~15ms per chunk), high semantic retrieval accuracy, and completely offline."),
        ("RAG Orchestrator", "LangChain (LCEL)", "Declarative LangChain Expression Language for prompt piping, output parsing, and interchangeable LLM providers."),
        ("LLM Engine", "OpenAI / Gemini / Ollama + Built-in Fallback", "Multi-provider architecture. Built-in offline Grounded Policy Analyst runs with zero external friction if keys are omitted."),
        ("Backend API", "FastAPI + Pydantic v2", "High-performance async Python web framework with auto Swagger UI (/docs), strict validation, and CORS support."),
        ("Frontend UI", "Streamlit", "Rapid glassmorphic dashboard with live vector cloud telemetry, document inspection (raw vs clean), and demographic filters.")
    ]
    
    for row_idx, (layer, tech, rationale) in enumerate(tech_data):
        row = tech_table.add_row()
        bg = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, text in enumerate([layer, tech, rationale]):
            c = row.cells[col_idx]
            c.width = widths[col_idx]
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if col_idx == 0:
                r.bold = True
                
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # Section 4: Step-by-Step Implementation Breakdown
    h4 = doc.add_heading("4. Step-by-Step Implementation Breakdown", level=1)
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(6)
    
    steps = [
        ("Step 1: PDF Ingestion & Regex Noise Cleaning (src/ingestion.py)",
         "Legislative bills downloaded from Congress contain recurring noise like running headers ('118TH CONGRESS'), footers, and left margin line numbers (1 through 25 on every single page). If embedded directly, vector search clusters around margin numbers or header text rather than actual policy provisions.\n\n"
         "Implementation:\n"
         "In LegislativeTextCleaner, compiled regular expressions strip these artifacts deterministically:\n"
         "• HEADER_PATTERNS: Matches congressional session marks and bill IDs.\n"
         "• FOOTER_PATTERNS: Removes page number footers.\n"
         "• LINE_NUMBER_PATTERN: Regex r'^\\s*([1-9]|[12][0-9])\\s+(?=[A-Za-z(])' removes the 1-25 margin numbers without touching numbers inside policy sentences (e.g. '$75,000' or '40 employees' remain untouched).\n"
         "• Section detector: Detects occurrences like 'SECTION 3. MICRO-ENTERPRISE TRANSITION GRANTS' to track section names per page.\n\n"
         "Interviewer Explanation: 'I built a dedicated sanitizer class that strips away congressional noise while preserving the legal numbers that actually matter. In our Document Inspector, this reduces noisy characters by 8% to 15% and ensures that embeddings only index pure legal prose.'"),
         
        ("Step 2: Context-Aware Recursive Chunking & Metadata Tagging (src/chunker.py)",
         "If you split text by arbitrary character counts (e.g. every 500 characters), a statutory section sentence granting a $2,400 subsidy might get split between two chunks, destroying the semantic link between the citizen qualification and the dollar amount.\n\n"
         "Implementation:\n"
         "LegislativeChunker uses LangChain's RecursiveCharacterTextSplitter:\n"
         "• Chunk Size: 1,000 characters with 200 character overlap.\n"
         "• Custom Hierarchical Separators: ['\\nSECTION ', '\\nSec. ', '\\n\\n', '\\n', '. ', '; ', ' ', '']\n"
         "• Metadata Preservation: Each chunk is wrapped with a deterministic chunk ID ({source}#p{page_number}#c{chunk_index:03d}) along with page_number, section, char_count, and word_count.\n\n"
         "Interviewer Explanation: 'Instead of blindly chopping the text into fixed-length blocks, my chunker prioritizes legal section headers. If a section is too long, it cascades down to paragraphs, then sentences. Most importantly, every chunk retains the exact page number and section title in its metadata for 100% auditability.'"),
         
        ("Step 3: Dense Embeddings & Persistent Vector Storage (src/vectorstore.py)",
         "Vector storage needs to be fast, persistent across restarts, and run locally without requiring expensive cloud subscriptions or sending confidential draft legislation to external APIs.\n\n"
         "Implementation:\n"
         "VectorStoreManager wraps ChromaDB and HuggingFace:\n"
         "• Embedding Model: sentence-transformers/all-MiniLM-L6-v2 converts text chunks into 384-dimensional dense vectors with L2 normalization.\n"
         "• Persistent ChromaDB Client: Stores embeddings in an on-disk SQLite/DuckDB index at ./db.\n"
         "• Similarity Search with Relevance Scoring: Executes cosine similarity search returning top-k chunks along with confidence scores between 0.0 and 1.0.\n"
         "• Batch Upserts: Ingests document chunks with deterministic IDs to prevent duplicate chunk storage.\n\n"
         "Interviewer Explanation: 'I chose ChromaDB with MiniLM embeddings because it provides offline, 384-dimensional dense vector search with sub-20ms retrieval times on standard CPUs. We don't have to spin up cloud vector instances, and data stays completely private.'"),
         
        ("Step 4: Grounded Demographic RAG Chain & Hallucination Guardrails (src/rag_chain.py)",
         "Standard LLMs hallucinate plausible-sounding legal advice when asked about things that aren't in the bill. Furthermore, statutory language is dense; citizens need to know what a bill means for them specifically (e.g. as a small business owner or a retiree).\n\n"
         "Implementation:\n"
         "LegislativeRAGChain combines prompt engineering, LCEL, and fallback safety:\n"
         "• Targeted Demographic Prompting: Focuses analysis on the selected demographic (e.g. Small Business Owners, Displaced Energy Workers, Senior Citizens).\n"
         "• Strict Groundedness Rule: Mandates: 'Base your analysis EXCLUSIVELY on the provided legislative text context below. If the context does not contain the answer, you MUST state: I don't know based on the provided legislative text.'\n"
         "• Multi-Model Dynamic Adapter: Supports OpenAI, Ollama, and a built-in LocalFallbackGroundedAnalyst ensuring 100% functionality with zero external API keys.\n"
         "• Structured Output: Returns Executive Summary, Demographic Impact Analysis, and Statutory Citations.\n\n"
         "Interviewer Explanation: 'I designed the RAG chain around strict source grounding. If a user asks about Mars space exploration in an energy bill, the guardrail detects the relevance mismatch and immediately returns I don't know based on the provided text, preventing hallucinations.'"),
         
        ("Step 5: Production REST API (src/api.py)",
         "A machine learning pipeline is only useful if other applications can communicate with it reliably.\n\n"
         "Implementation:\n"
         "Built with FastAPI and Pydantic v2:\n"
         "• GET /health: System health and vector database statistics.\n"
         "• GET /demographics: Available demographic profiles.\n"
         "• GET /documents: List ingested bills and chunk counts.\n"
         "• POST /query: Executes RAG pipeline and returns structured citations.\n"
         "• POST /upload: Multipart PDF upload that extracts, cleans, chunks, and indexes in real-time.\n\n"
         "Interviewer Explanation: 'I exposed the entire RAG pipeline through FastAPI with Pydantic schemas. It features automatic OpenAPI documentation at /docs and an endpoint that ingests, cleans, chunks, and indexes a multi-page PDF on the fly.'"),
         
        ("Step 6: Interactive Dashboard & Document Inspector (frontend/app.py)",
         "Stakeholders and interviewers need an intuitive visual interface to see the pipeline in action.\n\n"
         "Implementation:\n"
         "Streamlit dashboard featuring:\n"
         "• Policy Analysis Module: Demographic selector, Top-K slider, preset inquiry chips, grounded response view with citation badges.\n"
         "• Document Inspector: Side-by-side comparison of raw PDF extraction vs cleaned text with character reduction metrics.\n"
         "• Document Ingestion: Drag-and-drop PDF uploader with live indexing.\n"
         "• Demographic Targeting: Visual demographic profiles with one-click inquiry triggers.\n"
         "• Vector Engine Config: ChromaDB collection telemetry and index reset controls.")
    ]
    
    for title, text in steps:
        doc.add_heading(title, level=2)
        p = doc.add_paragraph(text)
        p.paragraph_format.space_after = Pt(8)
        
    # Section 5: Common Interview Questions & Answers
    h5 = doc.add_heading("5. Interviewer Q&A: Master the Hard Questions", level=1)
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(6)
    
    qas = [
        ("Q1: Why did you choose ChromaDB instead of Pinecone or FAISS?",
         "Pinecone is a managed cloud service which introduces network latency, recurring cost, and privacy concerns when dealing with draft legislation. FAISS is extremely fast for in-memory vector search, but it lacks built-in metadata filtering and disk persistence out of the box. ChromaDB provided the sweet spot: it runs embedded, persists automatically to SQLite/DuckDB, supports rich metadata querying (page numbers, section titles), and requires zero external infrastructure."),
         
        ("Q2: Why use all-MiniLM-L6-v2 instead of OpenAI text-embedding-3-small?",
         "MiniLM produces 384-dimensional dense vectors with high semantic accuracy on legal and domain texts while running entirely on local CPU in ~15 milliseconds. It avoids external API latency, rate limits, and per-token API costs during bulk PDF ingestion. If we scaled to a production system with hundreds of thousands of bills, we could easily benchmark against BGE-large or fine-tune an embedding model on legal corpus data."),
         
        ("Q3: How does your chunking strategy handle cross-section references?",
         "In legislative bills, sections frequently reference other sections (e.g. 'as defined in Section 2(b)'). I addressed this in two ways: first, using a 200-character overlap between chunks to keep adjacent context intact; second, embedding the Section title directly into the chunk metadata, ensuring that the retriever knows both the origin section and the cited context."),
         
        ("Q4: How would you scale this architecture to handle 100,000 bills?",
         "To scale to enterprise volume:\n"
         "1. Decouple ingestion with an asynchronous worker queue (Celery + Redis) so large PDFs process in the background.\n"
         "2. Migrate vector storage to a distributed engine like Milvus or Qdrant with HNSW indexing and sharding.\n"
         "3. Add a hybrid search layer combining BM25 keyword search with dense vector search (Reciprocal Rank Fusion) so exact bill numbers (like 'H.R. 4082') match deterministically.\n"
         "4. Implement semantic caching (Redis) for frequently asked policy questions to reduce LLM computation by 40-50%."),
         
        ("Q5: How do you evaluate retrieval quality in this pipeline?",
         "I validated retrieval across three metrics:\n"
         "1. Keyword Recall: Verifying that key policy figures (e.g. '$75,000 grant', '$2,400 stipend', '5 percent utility cap') appear in the top-4 retrieved snippets.\n"
         "2. Negative Recall (Guardrail Test): Querying out-of-domain topics (e.g. 'Mars space mission budget') and verifying that the system returns 'I don't know' without hallucinating.\n"
         "3. Automated Pytest Suites: Automated tests verifying HTTP 200 responses, schema adherence, and chunk count consistency.")
    ]
    
    for q, a in qas:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(q)
        r_q.bold = True
        r_q.font.color.rgb = RGBColor(30, 58, 138) # Blue 900
        r_q.font.size = Pt(11.5)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_after = Pt(6)
        r_a = p_a.add_run(a)
        r_a.font.size = Pt(10.5)
        
    # Section 6: Future Production Roadmap
    h6 = doc.add_heading("6. Future Production Roadmap", level=1)
    h6.paragraph_format.space_before = Pt(14)
    h6.paragraph_format.space_after = Pt(6)
    
    doc.add_paragraph(
        "1. Hybrid Search (BM25 + Dense Vectors): Combine lexical and semantic search using Reciprocal Rank Fusion (RRF) for exact statutory code lookups.\n"
        "2. Hierarchical Knowledge Graph (GraphRAG): Map cross-references between bills, amendments, and public laws using Neo4j.\n"
        "3. Multi-Agent Comparative Policy Analysis: Deploy an agentic team where one agent represents small businesses, another represents municipal fiscal budgets, and an arbiter highlights conflicting interests.\n"
        "4. Automated Redlining & Diff Detection: Ingest amended bills and automatically generate redline diffs showing what specific lines were added or stricken."
    )
    
    # Save document
    doc.save(output_path)
    print(f"[+] Successfully generated Word Document: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "LegiGraph_Project_Explanation_Interview_Guide.docx"
    build_docx(out_file)
