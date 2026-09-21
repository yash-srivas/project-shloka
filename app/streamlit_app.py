"""
Streamlit Demo Application for Sanskrit Shloka Analysis RAG System.
Features:
- Sidebar with Chapter metadata & Shloka Selector
- Main Sanskrit Shloka Viewer with transliteration
- 7 Dedicated Tabs for the 7 Ayurvidya Steps
- Step-specific Retrieved Context Inspector (evidence grounding)
- One-click 'Run 7-Step Analysis' button with progress indicators
- Interactive Grounded Chatbot aware of the selected Shloka and RAG knowledge
"""

import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from src.config import CHROMA_COLLECTION_NAME, LLM_PROVIDER, LLM_MODEL, DEBUG_MODE
from src.chunker import build_and_save_processed_data
from src.vector_store import ChromaVectorStore
from src.retriever import ShlokaRetriever
from src.pipeline import ShlokaPipelineOrchestrator
from src.llm import LLMClient
from src.prompts import STEPS_CONFIG

# Configure Streamlit Page
st.set_page_config(
    page_title="Sanskrit Shloka Analysis RAG — Sushruta Samhita",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for refined aesthetics & readable Devanagari
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Sanskrit:ital@0;1&family=Inter:wght@300;400;600;700&display=swap');
    
    .shloka-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-left: 6px solid #f59e0b;
        padding: 24px;
        border-radius: 12px;
        color: #f8fafc;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .shloka-devanagari {
        font-family: 'Tiro Devanagari Sanskrit', serif;
        font-size: 26px;
        line-height: 1.8;
        font-weight: 600;
        color: #fbbf24;
        white-space: pre-line;
    }
    .shloka-translit {
        font-family: 'Inter', sans-serif;
        font-style: italic;
        color: #94a3b8;
        font-size: 15px;
        margin-top: 12px;
        white-space: pre-line;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    .badge-primary { background: #3b82f6; color: white; }
    .badge-gold { background: #d97706; color: white; }
    .badge-green { background: #10b981; color: white; }
    
    .retrieved-card {
        background: #f1f5f9;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 13.5px;
        color: #1e293b;
    }
    .step-output-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 10px;
        font-size: 15px;
        line-height: 1.7;
        white-space: pre-wrap;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# 1. State & Resource Initialization
@st.cache_resource
def get_shlokas():
    shlokas, _ = build_and_save_processed_data()
    return shlokas

@st.cache_resource
def get_retriever():
    return ShlokaRetriever()

@st.cache_resource
def get_orchestrator():
    return ShlokaPipelineOrchestrator()

shlokas_list = get_shlokas()
retriever = get_retriever()
orchestrator = get_orchestrator()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. Sidebar Controls
with st.sidebar:
    st.title("📖 Sushruta Samhita")
    st.caption("Sanskrit/Ayurveda Shloka Analysis System")
    st.divider()

    st.markdown("**Sthāna:** Nidana Sthana (निदानस्थानम्)")
    st.markdown("**Chapter 1:** Vatavyadhi Nidana (वातव्याधिनिदानम्)")
    
    st.divider()
    st.subheader("Select Shloka")

    # Shloka selector options
    options = {
        f"श्लोक #{s.shloka_number_display} — {s.english_title or s.text[:30]}...": s 
        for s in shlokas_list
    }
    selected_label = st.selectbox(
        "Choose a verse to analyze:",
        options=list(options.keys()),
        index=0
    )
    current_shloka = options[selected_label]

    st.divider()
    st.subheader("System Status")
    st.write(f"**Chroma Collection:** `{CHROMA_COLLECTION_NAME}`")
    st.write(f"**Vector Store Count:** {orchestrator.retriever.vector_store.count()} chunks")
    st.write(f"**LLM Provider:** `{LLM_PROVIDER}`")
    st.write(f"**Model:** `{LLM_MODEL}`")

    if st.button("Clear Step Cache"):
        orchestrator.cache.clear_cache(current_shloka.id)
        st.success("Cache cleared for this shloka.")
        st.rerun()

# 3. Main Header & Shloka Presentation
st.title("🌿 Sanskrit & Ayurveda Shloka Analysis")
st.markdown("Automated 7-step analysis grounded in Sushruta Samhita via RAG (Retrieval-Augmented Generation).")

# Shloka Header Box
st.markdown(f"""
<div class="shloka-box">
    <div>
        <span class="badge badge-gold">Chapter 1</span>
        <span class="badge badge-primary">श्लोक {current_shloka.shloka_number_display}</span>
        <span class="badge badge-green">{current_shloka.source}</span>
    </div>
    <div style="margin-top: 14px;" class="shloka-devanagari">{current_shloka.text}</div>
    <div class="shloka-translit">{current_shloka.transliteration or ''}</div>
    <div style="margin-top: 8px; color: #cbd5e1; font-size: 14px;"><strong>Topic:</strong> {current_shloka.english_title or 'Vatavyadhi'}</div>
</div>
""", unsafe_allow_html=True)

# 4. Action Button
col_btn, col_refresh = st.columns([3, 2])
with col_btn:
    run_clicked = st.button("⚡ Run 7-Step Analysis", type="primary", use_container_width=True)
with col_refresh:
    force_refresh = st.checkbox("Force Regenerate (Bypass Cache)", value=False)

# Check or Run Pipeline
if run_clicked or force_refresh:
    with st.spinner("Analyzing Shloka across all 7 steps with RAG retrieval..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def on_step_progress(step_num: int, name_sa: str, msg: str):
            progress_bar.progress(int((step_num / 7.0) * 100))
            status_text.text(f"Step {step_num}/7: {name_sa} — {msg}")

        pipeline_result = orchestrator.run_analysis(
            shloka=current_shloka,
            force_refresh=force_refresh,
            progress_callback=on_step_progress
        )
        progress_bar.empty()
        status_text.empty()
        st.session_state[f"result_{current_shloka.id}"] = pipeline_result
        st.success(f"Analysis complete in {pipeline_result.execution_time_seconds}s!")

# Fetch result from session or cache
pipeline_result = st.session_state.get(f"result_{current_shloka.id}")
if not pipeline_result:
    cached_steps = orchestrator.cache.get_all_steps(shloka_id=current_shloka.id)
    if cached_steps:
        from src.schemas import PipelineResult
        pipeline_result = PipelineResult(
            shloka_id=current_shloka.id,
            shloka_number=current_shloka.shloka_number,
            shloka_text=current_shloka.text,
            steps=cached_steps,
            execution_time_seconds=0.0,
            cached=True
        )

# 5. Seven Tabs for the Seven Steps
tab_titles = [
    "1. संप्रदानम्",
    "2. पदविभागः",
    "3. अन्वयः",
    "4. अन्वयार्थः",
    "5. भावार्थः",
    "6. पदकृत्यम्",
    "7. ध्वनितार्थः"
]
tabs = st.tabs(tab_titles)

for step_num, tab in enumerate(tabs, 1):
    step_meta = STEPS_CONFIG[step_num]
    with tab:
        st.subheader(f"{step_meta['name_sa']} — {step_meta['name_en']}")
        st.caption(step_meta['desc'])

        step_data = pipeline_result.steps.get(step_num) if pipeline_result else None

        if step_data:
            # Main Output
            st.markdown(f'<div class="step-output-box">{step_data.output}</div>', unsafe_allow_html=True)

            # Retrieved Context Expander
            with st.expander(f"🔍 Inspect Retrieved RAG Context for Step {step_num} ({len(step_data.retrieved_contexts)} sources)"):
                if step_data.retrieved_contexts:
                    for idx, ctx in enumerate(step_data.retrieved_contexts, 1):
                        sim = f" (Score: {ctx.similarity_score})" if ctx.similarity_score else ""
                        st.markdown(f"""
                        <div class="retrieved-card">
                            <strong>[{idx}] {ctx.source} — Shloka {ctx.shloka_number or 'Methodology'} ({ctx.content_type}){sim}</strong><br/>
                            <em>{ctx.text.replace(chr(10), ' ')}</em>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No external vector context required or retrieved.")
        else:
            st.info("Step output not yet generated. Click **'Run 7-Step Analysis'** above to process this verse.")

# 6. Interactive Grounded Chatbot
st.divider()
st.subheader("💬 Shloka Q&A Assistant (RAG Chatbot)")
st.caption("Ask questions about this shloka, its grammar, clinical indications, or philosophy. Responses are strictly grounded in retrieved Sushruta Samhita context.")

# Display prior chat messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("Retrieved Sources"):
                for src in msg["sources"]:
                    st.caption(f"• {src}")

user_query = st.chat_input("Ask a question about the current shloka (e.g., 'What diseases does this Vāyu cause?')")

if user_query:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # RAG Retrieval for the query combined with selected shloka context
    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant passages and synthesizing answer..."):
            rag_query = f"{current_shloka.text} {user_query}"
            chat_retrieval = retriever.retrieve(query=rag_query, top_k=3)

            context_items = [f"[{r.source} Shloka {r.shloka_number or 'Gen'}]: {r.text}" for r in chat_retrieval]
            context_block = "\n\n".join(context_items)

            chat_prompt = (
                f"You are an expert Sanskrit and Ayurveda tutor assisting a student studying Sushruta Samhita, Vatavyadhi Nidana.\n"
                f"CURRENT SELECTED SHLOKA: {current_shloka.text}\n\n"
                f"RETRIEVED KNOWLEDGE:\n{context_block}\n\n"
                f"STUDENT QUESTION: {user_query}\n\n"
                f"Provide a clear, helpful, grounded answer based strictly on the retrieved knowledge and current shloka. "
                f"If the information is not in the text, clearly state that the provided text does not contain that detail."
            )

            llm = LLMClient()
            answer = llm.generate(prompt=chat_prompt)
            st.markdown(answer)

            sources_list = [f"{r.source} - Shloka {r.shloka_number or 'Methodology'}" for r in chat_retrieval]
            if sources_list:
                with st.expander("Grounded Sources"):
                    for s in sources_list:
                        st.caption(f"• {s}")

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "sources": sources_list
            })
