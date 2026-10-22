"""
LegiGraph Interactive Web Dashboard - Authentic Umbrel.com Design & Architecture.
- Navigation solely in the sidebar with appropriate, comfortable spacing and no divider lines
- Minimal top header bar with breadcrumb hierarchy and live ChromaDB status badge
- Ultra-Clean Minimalist Obsidian & Zinc Surfaces (#000000, #0e0e11, #18181b)
- Editorial Typography: Inter & Playfair Display accents
- 100% clickable native buttons for all module switches
"""

import sys
import os
from pathlib import Path
import streamlit as st

# Setup Python paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings, DATA_DIR, DEFAULT_PDF_PATH
from src.vectorstore import VectorStoreManager
from src.rag_chain import LegislativeRAGChain
from src.ingestion import extract_and_clean_pdf
from src.chunker import LegislativeChunker
from scripts.generate_sample_bill import create_sample_legislative_bill, create_sample_healthcare_bill

# Page configuration
st.set_page_config(
    page_title="LegiGraph | Legislative Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Umbrel Design System Stylesheet
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@1,500;1,600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: #000000 !important;
        color: #f4f4f5 !important;
        letter-spacing: -0.011em;
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1300px;
    }

    /* Ambient Subtle Mesh Background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: 
            radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.05) 0%, transparent 65%),
            radial-gradient(circle at 85% 90%, rgba(245, 158, 11, 0.03) 0%, transparent 55%),
            radial-gradient(circle at 15% 75%, rgba(59, 130, 246, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* Top Header Bar */
    .top-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 16px;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    }

    /* Primary & Secondary Buttons for Main App */
    div[data-testid="stButton"] button {
        border-radius: 9999px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
        white-space: nowrap !important;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background: #ffffff !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border: 1px solid #ffffff !important;
        box-shadow: 0 4px 18px rgba(255, 255, 255, 0.2) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: #e4e4e7 !important;
        transform: translateY(-1px) scale(1.02) !important;
        color: #000000 !important;
    }

    div[data-testid="stButton"] button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.04) !important;
        color: #a1a1aa !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.22) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }

    /* =========================================================================
       SIDEBAR NAVIGATION STYLING (Generous, Appropriate Spacing & Alignment)
       ========================================================================= */
    section[data-testid="stSidebar"] {
        background: rgba(9, 9, 12, 0.85) !important;
        backdrop-filter: blur(28px) saturate(190%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(190%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Appropriate vertical gap between sidebar elements */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.65rem !important;
    }

    /* Completely eliminate any horizontal separation lines/rules */
    section[data-testid="stSidebar"] hr {
        display: none !important;
    }

    /* Sidebar Section Titles with generous top & bottom margins */
    .sidebar-section-title {
        font-size: 0.72rem;
        font-weight: 600;
        color: #71717a;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0 6px;
        margin-top: 24px;
        margin-bottom: 10px;
    }

    /* Navigation Buttons - Clear, Comfortable Spacing between Items */
    section[data-testid="stSidebar"] div[data-testid="stButton"] {
        margin: 0 0 8px 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        border-radius: 11px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 10px 14px !important;
        margin: 0 !important;
        min-height: 44px !important;
        height: 44px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        align-items: center !important;
        border: none !important;
        box-shadow: none !important;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button div[data-testid="stMarkdownContainer"] {
        width: 100% !important;
        text-align: left !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button div[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
        text-align: left !important;
        font-size: 0.88rem !important;
        line-height: 1.25 !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }

    /* Active Nav Item */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
        background: #ffffff !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 2px 12px rgba(255, 255, 255, 0.14) !important;
    }

    /* Inactive Nav Item: Transparent, subtle hover, no borders or separation lines */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {
        background: transparent !important;
        color: #a1a1aa !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.07) !important;
        color: #ffffff !important;
    }

    /* Umbrel Brand Card */
    .umbrel-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 13px 15px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        margin-bottom: 8px;
        backdrop-filter: blur(16px);
    }

    .umbrel-icon-box {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: #ffffff;
        color: #000000;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.10rem;
        font-weight: 700;
        box-shadow: 0 3px 12px rgba(255, 255, 255, 0.18);
    }

    /* Sidebar Telemetry Box */
    .sidebar-telemetry-box {
        padding: 14px 16px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        backdrop-filter: blur(12px);
        margin-top: 4px;
        margin-bottom: 4px;
    }

    /* Sidebar Active Bill Card */
    .sidebar-bill-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        padding: 9px 13px;
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 0.80rem;
        color: #d4d4d8;
        transition: all 0.15s ease;
    }
    .sidebar-bill-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.12);
    }

    .badge-gold {
        background: linear-gradient(180deg, #fbbf24 0%, #d97706 100%);
        color: #000000;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 9999px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        display: inline-block;
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e4e4e7;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Umbrel Editorial Typography */
    .umbrel-hero-title {
        font-size: 2.35rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1.15;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .umbrel-hero-editorial {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #e4e4e7;
        font-weight: 500;
    }

    .umbrel-hero-sub {
        font-size: 1.02rem;
        color: #a1a1aa;
        max-width: 680px;
        line-height: 1.5;
        margin-bottom: 24px;
    }

    /* Umbrel Cards with Inset Border */
    .umbrel-card {
        background: rgba(18, 18, 22, 0.65);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.7);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .umbrel-card:hover {
        border-color: rgba(255, 255, 255, 0.22);
        transform: translateY(-2px);
    }

    /* Citation Box */
    .citation-block {
        background: rgba(14, 14, 18, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 3px solid #ffffff;
        border-radius: 12px;
        padding: 14px 18px;
        margin-top: 10px;
        font-size: 0.88rem;
        color: #d4d4d8;
        line-height: 1.6;
    }

    /* Telemetry Numbers */
    .metric-box {
        background: rgba(18, 18, 22, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 18px 20px;
        text-align: left;
        min-height: 96px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-val {
        font-size: 2.1rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .metric-lbl {
        font-size: 0.78rem;
        color: #71717a;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }

    .app-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.6);
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State & Singletons
@st.cache_resource
def get_managers():
    if not DEFAULT_PDF_PATH.exists():
        create_sample_legislative_bill(str(DEFAULT_PDF_PATH))
    vstore = VectorStoreManager()
    rag_chain = LegislativeRAGChain(vector_store_manager=vstore)
    chunker = LegislativeChunker()
    return vstore, rag_chain, chunker

vstore, rag_chain, chunker = get_managers()

# Session State Defaults
if "selected_demographic" not in st.session_state:
    st.session_state["selected_demographic"] = "Small Business Owners"
if "top_k_chunks" not in st.session_state:
    st.session_state["top_k_chunks"] = 4
if "user_query_input" not in st.session_state:
    st.session_state["user_query_input"] = "What grants and employee thresholds are available for small businesses?"
if "active_nav_tab" not in st.session_state:
    st.session_state["active_nav_tab"] = "Policy Analysis"

# Navigation Modules
NAV_MODULES = [
    ("⚖️ Policy Analysis", "Policy Analysis"),
    ("📑 Document Inspector", "Document Inspector"),
    ("📥 Document Ingestion", "Document Ingestion"),
    ("👥 Demographic Targeting", "Demographic Targeting"),
    ("🎛️ Search Engine Config", "Search Engine Config")
]

# ==============================================================================
# MINIMAL TOP HEADER (Breadcrumb & Live Status - No Top Navigation)
# ==============================================================================
stats = vstore.get_stats()
st.markdown(f"""
<div class="top-header-bar">
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.25rem;">⚖️</span>
        <span style="font-size: 1.15rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">LegiGraph</span>
        <span style="color: #52525b; font-size: 0.9rem;">/</span>
        <span style="color: #e4e4e7; font-size: 0.92rem; font-weight: 600;">{st.session_state['active_nav_tab']}</span>
        <span class="badge-gold" style="margin-left: 4px;">v1.0</span>
    </div>
    <div>
        <span class="badge-pill" style="color: #10b981; border-color: rgba(16, 185, 129, 0.3); margin: 0;">
            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #10b981; margin-right: 6px;"></span>
            {stats['total_chunks_indexed']} Chunks Active
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR: PRIMARY NAVIGATION & COMPACT INGESTED BILLS
# ==============================================================================
with st.sidebar:
    # Sidebar Brand
    st.markdown(f"""
    <div class="umbrel-brand">
        <div class="umbrel-icon-box">⚖️</div>
        <div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #ffffff; line-height: 1.2;">LegiGraph</div>
            <div style="font-size: 0.72rem; color: #a1a1aa;">Statutory Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-title' style='margin-top: 20px;'>Navigation Modules</div>", unsafe_allow_html=True)

    # Sidebar Navigation Buttons - Clean, 100% Clickable, Seamless, Generous Spacing
    for idx, (label, mod_key) in enumerate(NAV_MODULES):
        is_active = (st.session_state["active_nav_tab"] == mod_key)
        btn_kind = "primary" if is_active else "secondary"
        if st.button(label, key=f"side_btn_{idx}", type=btn_kind, use_container_width=True):
            st.session_state["active_nav_tab"] = mod_key
            st.rerun()

    # Vector Cloud Box - Proper Section Margin, No Separation Lines
    st.markdown("<div class='sidebar-section-title'>Vector Cloud</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-telemetry-box">
        <div style="font-size: 0.68rem; color: #71717a; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">ChromaDB Vector Cloud</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
            <span style="font-size: 0.80rem; color: #e4e4e7; font-weight: 500;">Persistent Chunks</span>
            <span style="font-size: 0.86rem; color: #ffffff; font-weight: 700;">{stats['total_chunks_indexed']}</span>
        </div>
        <div style="font-size: 0.70rem; color: #10b981; margin-top: 6px; display: flex; align-items: center; gap: 6px;">
            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #10b981; box-shadow: 0 0 6px #10b981;"></span> Embeddings Active
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-title'>Active Bills</div>", unsafe_allow_html=True)
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    for pdf in pdf_files:
        st.markdown(f"""
        <div class="sidebar-bill-card">
            <div style="display: flex; align-items: center; gap: 8px; overflow: hidden;">
                <span>📄</span>
                <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{pdf.name}</span>
            </div>
            <span class="badge-pill" style="margin: 0; padding: 2px 7px; font-size: 0.68rem; color: #a1a1aa; border-color: rgba(255,255,255,0.08);">PDF</span>
        </div>
        """, unsafe_allow_html=True)


# Determine active module
current_tab = st.session_state["active_nav_tab"]

# ==============================================================================
# SECTION 1: POLICY IMPACT ANALYSIS
# ==============================================================================
if current_tab == "Policy Analysis":
    st.markdown("""
    <div class="umbrel-hero-title">Public policy, decoded for <span class="umbrel-hero-editorial">everyone</span>.</div>
    <div class="umbrel-hero-sub">Dense legislative acts and Congressional bills translated into verifiable, demographic-specific statutory impacts in seconds.</div>
    """, unsafe_allow_html=True)
    
    col_ctrl1, col_ctrl2 = st.columns([3, 1])
    with col_ctrl1:
        st.session_state["selected_demographic"] = st.selectbox(
            "Target Demographic Focus:",
            options=settings.TARGET_DEMOGRAPHICS,
            index=settings.TARGET_DEMOGRAPHICS.index(st.session_state["selected_demographic"]) if st.session_state["selected_demographic"] in settings.TARGET_DEMOGRAPHICS else 0
        )
    with col_ctrl2:
        st.session_state["top_k_chunks"] = st.slider(
            "Context Chunks (Top-K):",
            min_value=2,
            max_value=8,
            value=st.session_state["top_k_chunks"]
        )

    # Preset Questions Styled like Umbrel Tags in a Balanced 2x3 Grid
    st.markdown("<div style='font-size: 0.78rem; color: #71717a; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 8px 0;'>Suggested Inquiries:</div>", unsafe_allow_html=True)
    sample_queries = [
        ("Small Business Grants", "What clean energy grants, subsidy percentages, and employee size caps exist for small businesses?"),
        ("Worker Transition", "What wage guarantees, monthly stipends, and educational subsidies are provided to displaced energy workers?"),
        ("Utility Bill Caps", "How are residential energy utility bills capped as a percentage of income for low-income households?"),
        ("Rural Solar Credits", "What annual tax credit per acre is offered to rural farmers for community solar co-ops?"),
        ("Senior Medicare Caps", "What is the monthly prescription co-pay cap for seniors on insulin and chronic medications?"),
        ("Hallucination Test", "What are the safety protocols and budget allocations for Mars space exploration rockets in this bill?")
    ]
    
    col_chips1 = st.columns(3)
    col_chips2 = st.columns(3)
    for idx, (label, prompt_text) in enumerate(sample_queries):
        target_col = col_chips1[idx] if idx < 3 else col_chips2[idx - 3]
        with target_col:
            if st.button(label, key=f"chip_{idx}", use_container_width=True):
                st.session_state["user_query_input"] = prompt_text
                st.rerun()

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # Query Input
    query_text = st.text_area(
        "Statutory Inquiry:",
        value=st.session_state.get("user_query_input", ""),
        height=95,
        placeholder="Type a policy or statutory question regarding the bill..."
    )
    
    col_run, _ = st.columns([1.5, 3.5])
    with col_run:
        execute_analysis = st.button("Run Grounded Analysis", type="primary", use_container_width=True)

    if execute_analysis and query_text.strip():
        with st.spinner(f"Analyzing statutory provisions for {st.session_state['selected_demographic']}..."):
            result = rag_chain.query(
                question=query_text,
                demographic=st.session_state["selected_demographic"],
                top_k=st.session_state["top_k_chunks"]
            )
            
            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
            col_left, col_right = st.columns([3, 2])
            
            with col_left:
                st.markdown(f"""
                <div class="umbrel-card" style="padding: 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
                        <span class="badge-pill" style="margin: 0;">Target: {st.session_state['selected_demographic']}</span>
                        <span class="badge-pill" style="margin: 0; color: #10b981; border-color: rgba(16, 185, 129, 0.3);">● Grounded Analysis</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(result["answer"])
                
            with col_right:
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 1.05rem; font-weight: 700; color: #ffffff;">Audited Source Citations</span>
                    <span class="badge-pill">{len(result['sources'])} Chunks</span>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, src in enumerate(result["sources"], 1):
                    with st.expander(f"Citation #{idx}: {src['section']} (Page {src['page_number']})", expanded=(idx == 1)):
                        st.markdown(f"**Document:** `{src['source']}`")
                        st.markdown(f"**Page:** `{src['page_number']}` | **Score:** `{src['relevance_score']:.4f}`")
                        st.markdown(f"""
                        <div class="citation-block">
                            {src['snippet']}
                        </div>
                        """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 2: DOCUMENT INSPECTOR
# ==============================================================================
elif current_tab == "Document Inspector":
    st.markdown("""
    <div class="umbrel-hero-title">Inside the statutory <span class="umbrel-hero-editorial">text</span>.</div>
    <div class="umbrel-hero-sub">Inspect raw PDF document extraction alongside deterministic regex noise-reduction filters.</div>
    """, unsafe_allow_html=True)
    
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        st.warning("No PDF bills found in data/. Ingest or generate a bill first.")
    else:
        selected_file = st.selectbox("Select Bill to Inspect:", options=[p.name for p in pdf_files], index=0)
        selected_path = DATA_DIR / selected_file
        pages = extract_and_clean_pdf(str(selected_path))
        
        # Telemetry Numbers Row
        t1, t2, t3, t4 = st.columns(4)
        total_raw = sum(p["raw_length"] for p in pages)
        total_clean = sum(p["cleaned_length"] for p in pages)
        pct_reduced = ((total_raw - total_clean) / total_raw * 100) if total_raw > 0 else 0
        all_sections = []
        for p in pages:
            all_sections.extend(p["sections"])
            
        with t1:
            st.markdown(f"""<div class="metric-box"><div class="metric-val">{len(pages)}</div><div class="metric-lbl">Total Pages</div></div>""", unsafe_allow_html=True)
        with t2:
            st.markdown(f"""<div class="metric-box"><div class="metric-val">{total_raw:,}</div><div class="metric-lbl">Raw Characters</div></div>""", unsafe_allow_html=True)
        with t3:
            st.markdown(f"""<div class="metric-box"><div class="metric-val">{total_clean:,}</div><div class="metric-lbl">Clean Chars (-{pct_reduced:.1f}%)</div></div>""", unsafe_allow_html=True)
        with t4:
            st.markdown(f"""<div class="metric-box"><div class="metric-val">{len(all_sections)}</div><div class="metric-lbl">Sections Detected</div></div>""", unsafe_allow_html=True)
            
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        page_num = st.slider("Inspect Page:", min_value=1, max_value=len(pages), value=1)
        page_data = pages[page_num - 1]
        
        if page_data["sections"]:
            st.markdown("**Detected Statutory Headings:**")
            for sec in page_data["sections"]:
                st.markdown(f"<span class='badge-pill'>🏷️ {sec}</span>", unsafe_allow_html=True)
                
        col_clean, col_raw = st.columns(2)
        with col_clean:
            st.markdown("#### Clean Statutory Text (Noise Removed)")
            st.caption("Running headers, footers, page numbers, and line numbers removed.")
            st.text_area("Cleaned Content", value=page_data["cleaned_text"], height=380, key=f"c_view_{page_num}")
        with col_raw:
            st.markdown("#### Raw Text (PyMuPDF Extraction)")
            st.caption("Original text with congressional headers, footers & margin line numbers.")
            st.text_area("Raw Content", value=page_data["raw_text"], height=380, key=f"r_view_{page_num}")


# ==============================================================================
# SECTION 3: DOCUMENT INGESTION
# ==============================================================================
elif current_tab == "Document Ingestion":
    st.markdown("""
    <div class="umbrel-hero-title">Bring your bills <span class="umbrel-hero-editorial">home</span>.</div>
    <div class="umbrel-hero-sub">Upload legislative PDFs directly into your persistent local vector store with automatic chunking.</div>
    """, unsafe_allow_html=True)
    
    col_up1, col_up2 = st.columns([2, 1])
    
    with col_up1:
        st.markdown("#### Upload Legislative Bill (PDF)")
        uploaded_pdf = st.file_uploader("Drop a bill PDF here:", type=["pdf"])
        
        if uploaded_pdf is not None:
            if st.button("Ingest & Index Document", type="primary", use_container_width=True):
                with st.spinner("Extracting text, cleaning noise, chunking, and indexing..."):
                    dest_path = DATA_DIR / uploaded_pdf.name
                    with open(dest_path, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())
                        
                    pages = extract_and_clean_pdf(str(dest_path))
                    chunks = chunker.chunk_document_pages(pages)
                    vstore.batch_upload_chunks(chunks)
                    
                    st.success(f"Indexed '{uploaded_pdf.name}'! ({len(chunks)} chunks across {len(pages)} pages)")
                    st.rerun()

    with col_up2:
        st.markdown("#### Sample Bill Templates")
        st.caption("Generate pre-built multi-page legislative bills to test the pipeline:")
        if st.button("Generate Clean Energy Act (H.R. 4082)", use_container_width=True):
            create_sample_legislative_bill(str(DEFAULT_PDF_PATH))
            pages = extract_and_clean_pdf(str(DEFAULT_PDF_PATH))
            chunks = chunker.chunk_document_pages(pages)
            vstore.batch_upload_chunks(chunks)
            st.success("Indexed H.R. 4082 (5 Pages)!")
            st.rerun()
            
        if st.button("Generate Healthcare Act (S. 2190)", use_container_width=True):
            med_path = DATA_DIR / "sample_bill_healthcare_senior_care.pdf"
            create_sample_healthcare_bill(str(med_path))
            pages = extract_and_clean_pdf(str(med_path))
            chunks = chunker.chunk_document_pages(pages)
            vstore.batch_upload_chunks(chunks)
            st.success("Indexed S. 2190 (3 Pages)!")
            st.rerun()

    st.markdown("---")
    st.markdown("#### Document Catalog")
    files = list(DATA_DIR.glob("*.pdf"))
    for f in files:
        st.markdown(f"• **{f.name}** (`{f.stat().st_size / 1024:.1f} KB`)")


# ==============================================================================
# SECTION 4: DEMOGRAPHIC TARGETING
# ==============================================================================
elif current_tab == "Demographic Targeting":
    st.markdown("""
    <div class="umbrel-hero-title">Demographics in <span class="umbrel-hero-editorial">focus</span>.</div>
    <div class="umbrel-hero-sub">Tailored statutory interpretation vectors for specific economic and community groups.</div>
    """, unsafe_allow_html=True)
    
    profiles = [
        {
            "icon": "🏢",
            "name": "Small Business Owners",
            "scope": "Section 3: Micro-Enterprise Grants",
            "details": "Grants up to $75,000 for entities under 40 employees; 21-day expedited determination for minority- and women-owned businesses.",
            "query": "What are the exact eligibility thresholds and grant amounts for small businesses?"
        },
        {
            "icon": "🌾",
            "name": "Rural Residents & Farmers",
            "scope": "Section 5: Agricultural Solar Co-Ops",
            "details": "$1,200 annual property tax credit per acre for dedicated solar arrays; $500M community solar infrastructure fund.",
            "query": "What tax credits and co-op funding are available for rural agricultural producers?"
        },
        {
            "icon": "👷",
            "name": "Displaced Energy Workers",
            "scope": "Section 4: Displaced Worker Stipends",
            "details": "$2,400 monthly stipend for 18 months, 100% community college tuition reimbursement, and 24 months of continuing COBRA subsidies.",
            "query": "What wage guarantees, health subsidies, and tuition assistance are given to displaced energy workers?"
        },
        {
            "icon": "🏠",
            "name": "Low-Income Households",
            "scope": "Section 5: Residential Utility Caps",
            "details": "Direct block grants ensuring households under 200% federal poverty level spend no more than 5% of gross income on energy.",
            "query": "How will utility bills be capped for low-income households?"
        },
        {
            "icon": "👵",
            "name": "Senior Citizens (55+)",
            "scope": "Section 4(c) & S. 2190: Prescription Caps",
            "details": "Expedited bridge-to-pension option; $35 monthly co-pay ceiling on Medicare Part D insulin, inhalers, and cardiac medications.",
            "query": "What protections and prescription drug caps exist for senior citizens?"
        },
        {
            "icon": "🏛️",
            "name": "Municipalities & Local Gov",
            "scope": "Section 5 & S. 2190: Capital Grants",
            "details": "Up to $2.5M capital grants for critical access hospitals in counties under 35,000 residents; $350K library telehealth kiosks.",
            "query": "What hospital capital grants and public library telehealth funds are available to local governments?"
        }
    ]
    
    col_d1, col_d2 = st.columns(2)
    for idx, p in enumerate(profiles):
        target_col = col_d1 if idx % 2 == 0 else col_d2
        with target_col:
            st.markdown(f"""
            <div class="umbrel-card" style="min-height: 230px; margin-bottom: 10px;">
                <div class="app-icon">{p['icon']}</div>
                <div style="font-size: 1.20rem; font-weight: 700; color: #ffffff; margin-bottom: 3px;">
                    {p['name']}
                </div>
                <div style="font-size: 0.80rem; color: #a1a1aa; font-weight: 500; margin-bottom: 10px;">
                    {p['scope']}
                </div>
                <div style="font-size: 0.88rem; color: #d4d4d8; line-height: 1.55;">
                    {p['details']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Target {p['name']}", key=f"btn_target_{idx}", use_container_width=True):
                st.session_state["selected_demographic"] = p["name"]
                st.session_state["user_query_input"] = p["query"]
                st.session_state["active_nav_tab"] = "Policy Analysis"
                st.rerun()
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# SECTION 5: SEARCH CONFIGURATION
# ==============================================================================
elif current_tab == "Search Engine Config":
    st.markdown("""
    <div class="umbrel-hero-title">Vector engine <span class="umbrel-hero-editorial">controls</span>.</div>
    <div class="umbrel-hero-sub">Fine-tune retrieval hyperparameters, inspect ChromaDB collection telemetry, and maintain vector indices.</div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("#### Retrieval Parameters")
        st.session_state["top_k_chunks"] = st.slider(
            "Default Top-K Retrieved Chunks:",
            min_value=1,
            max_value=10,
            value=st.session_state["top_k_chunks"]
        )
        st.markdown(f"""
        <div class="umbrel-card">
            <div><b>Chunk Size:</b> <code>{settings.CHUNK_SIZE} characters</code></div>
            <div style="margin-top: 6px;"><b>Chunk Overlap:</b> <code>{settings.CHUNK_OVERLAP} characters</code></div>
            <div style="margin-top: 6px;"><b>Retriever Mode:</b> <code>Similarity Search with Relevance Scoring</code></div>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown("#### ChromaDB Persistent Telemetry")
        st.markdown(f"""
        <div class="umbrel-card">
            <div><b>Collection Name:</b> <code>{stats['collection_name']}</code></div>
            <div style="margin-top: 6px;"><b>Persistence Directory:</b> <code>{stats['persist_directory']}</code></div>
            <div style="margin-top: 6px;"><b>Indexed Chunks:</b> <b style="color: #ffffff;">{stats['total_chunks_indexed']}</b></div>
            <div style="margin-top: 6px;"><b>Embedding Model:</b> <code>{stats['embedding_model']}</code></div>
            <div style="margin-top: 6px;"><b>Vector Dimensions:</b> <code>384 dense floats</code></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Maintenance")
    if st.button("Rebuild ChromaDB Collection", type="secondary"):
        vstore.clear()
        if DEFAULT_PDF_PATH.exists():
            pages = extract_and_clean_pdf(str(DEFAULT_PDF_PATH))
            chunks = chunker.chunk_document_pages(pages)
            vstore.batch_upload_chunks(chunks)
        st.success("Vector store reset and re-indexed from default bills!")
        st.rerun()
