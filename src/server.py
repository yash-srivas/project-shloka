"""
FastAPI Server for Sanskrit Shloka Analysis RAG System.
Sushruta Samhita · Nidana Sthana · Chapter 1: Vatavyadhi Nidana

Serves:
- REST API for Shlokas, 7-Step Analysis, RAG Semantic Search, and Chatbot
- Static HTML/CSS/JS web frontend
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from src.config import (
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    LLM_PROVIDER,
    LLM_MODEL,
    DEBUG_MODE,
    get_config_summary,
    get_active_llm_config
)
from src.chunker import build_and_save_processed_data
from src.retriever import ShlokaRetriever
from src.vector_store import ChromaVectorStore
from src.pipeline import ShlokaPipelineOrchestrator
from src.llm import LLMClient
from src.prompts import STEPS_CONFIG
from src.schemas import ShlokaData, PipelineResult, RetrievalResult

from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Sushruta Samhita Shloka Analysis API",
    description="RAG-based Sanskrit & Ayurveda 7-Step Philological Analysis System",
    version="1.0.0"
)

# Enable CORS for local and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Singletons
_shlokas: Optional[List[ShlokaData]] = None
_retriever: Optional[ShlokaRetriever] = None
_orchestrator: Optional[ShlokaPipelineOrchestrator] = None

def get_shloka_catalog() -> List[ShlokaData]:
    global _shlokas
    if _shlokas is None:
        shlokas, _ = build_and_save_processed_data()
        _shlokas = shlokas
    return _shlokas

def get_retriever_instance() -> ShlokaRetriever:
    global _retriever
    if _retriever is None:
        _retriever = ShlokaRetriever()
    return _retriever

def get_orchestrator_instance() -> ShlokaPipelineOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ShlokaPipelineOrchestrator(retriever=get_retriever_instance())
    return _orchestrator

def find_shloka(shloka_id: str) -> Optional[ShlokaData]:
    """Find a shloka by ID, shloka number, display number, or shloka_N alias."""
    shlokas = get_shloka_catalog()
    query_str = str(shloka_id).strip().lower()
    # 1. Exact ID
    for s in shlokas:
        if s.id.lower() == query_str:
            return s
    # 2. Number or display match
    for s in shlokas:
        if str(s.shloka_number) == query_str or str(s.shloka_number_display).lower() == query_str:
            return s
        if query_str in [f"shloka_{s.shloka_number}", f"shloka_{s.shloka_number_display}".lower()]:
            return s
    return None

# Request/Response Models
class ChatRequest(BaseModel):
    shloka_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    shloka_id: str

# ─────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/status")
def get_system_status():
    """Return vector store size, configuration, and system readiness."""
    retriever = get_retriever_instance()
    count = retriever.vector_store.count()
    provider, model, _ = get_active_llm_config()
    return {
        "status": "ready",
        "chroma_collection": os.getenv("CHROMA_COLLECTION_NAME", CHROMA_COLLECTION_NAME),
        "indexed_chunks": count,
        "embedding_model": os.getenv("EMBEDDING_MODEL_NAME", EMBEDDING_MODEL_NAME),
        "llm_provider": provider,
        "llm_model": model,
        "steps_count": len(STEPS_CONFIG)
    }

@app.get("/api/shlokas")
def list_shlokas():
    """List all available shlokas in Chapter 1 with metadata and preview."""
    shlokas = get_shloka_catalog()
    return [
        {
            "id": s.id,
            "shloka_number": s.shloka_number,
            "shloka_number_display": s.shloka_number_display,
            "source": s.source,
            "sthana": s.sthana,
            "chapter": s.chapter,
            "english_title": s.english_title,
            "text": s.text,
            "transliteration": s.transliteration,
            "associated_pages": s.associated_pages
        }
        for s in shlokas
    ]

@app.get("/api/shlokas/{shloka_id}")
def get_shloka_detail(shloka_id: str):
    """Retrieve full details of a specific shloka, including pre-cached analysis if available."""
    target = find_shloka(shloka_id)
    if not target:
        raise HTTPException(status_code=404, detail=f"Shloka with ID '{shloka_id}' not found.")

    orchestrator = get_orchestrator_instance()
    provider, model, _ = get_active_llm_config()
    cached_steps = orchestrator.cache.get_all_steps(shloka_id=target.id, model=model)

    steps_payload = {}
    if cached_steps:
        steps_payload = {str(k): v.model_dump() for k, v in cached_steps.items()}

    formatted_config = {}
    for k, v in STEPS_CONFIG.items():
        formatted_config[str(k)] = {
            "step_number": k,
            "name_sa": v.get("name_sa", ""),
            "name_sanskrit": v.get("name_sa", ""),
            "name_en": v.get("name_en", ""),
            "name_english": v.get("name_en", ""),
            "desc": v.get("desc", ""),
            "description": v.get("desc", ""),
            "file": v.get("file", "")
        }

    return {
        "shloka": target.model_dump(),
        "steps_config": formatted_config,
        "is_cached": len(cached_steps) == 7,
        "cached_steps_count": len(cached_steps),
        "steps": steps_payload
    }

@app.post("/api/shlokas/{shloka_id}/analyze")
def run_shloka_analysis(shloka_id: str, force_refresh: bool = Query(default=False)):
    """Execute the full 7-step analysis pipeline on the given shloka."""
    target = find_shloka(shloka_id)
    if not target:
        raise HTTPException(status_code=404, detail=f"Shloka with ID '{shloka_id}' not found.")

    orchestrator = get_orchestrator_instance()
    result = orchestrator.run_analysis(shloka=target, force_refresh=force_refresh)

    llm = orchestrator.llm_client
    backend_called = "cache" if result.cached else ("mock" if llm.is_mock else llm.provider)
    print(
        f"[API DEBUG LOG] shloka_id={target.id} | provider={llm.provider} | "
        f"model={llm.model} | is_mock={llm.is_mock} | cache_used={result.cached} | "
        f"backend_called={backend_called}"
    )

    return {
        "shloka_id": result.shloka_id,
        "shloka_number": result.shloka_number,
        "shloka_text": result.shloka_text,
        "execution_time_seconds": result.execution_time_seconds,
        "cached": result.cached,
        "steps": {str(k): v.model_dump() for k, v in result.steps.items()}
    }

@app.delete("/api/shlokas/{shloka_id}/cache")
def clear_shloka_cache(shloka_id: str):
    """Clear cached step analysis for a specific shloka."""
    target = find_shloka(shloka_id)
    target_id = target.id if target else shloka_id
    orchestrator = get_orchestrator_instance()
    orchestrator.cache.clear_cache(shloka_id=target_id)
    return {"message": f"Cache cleared for shloka '{target_id}'", "shloka_id": target_id}

@app.get("/api/search")
def semantic_search(q: str = Query(..., min_length=1), top_k: int = Query(default=4, ge=1, le=10)):
    """Semantic vector search across ChromaDB collection."""
    retriever = get_retriever_instance()
    results = retriever.retrieve(query=q, top_k=top_k)
    return [r.model_dump() for r in results]

import re

def is_small_talk_or_greeting(text: str) -> bool:
    """Check if message is a greeting or conversational small talk rather than a study question."""
    raw = text.lower().strip()
    # Normalize repeated characters, e.g. "heyyyyyyyyyyyyyy" -> "hey", "hiiiiii" -> "hi"
    collapsed = re.sub(r'([a-z])\1{2,}', r'\1', raw)
    cleaned = "".join(ch for ch in collapsed if ch.isalnum() or ch.isspace()).strip()
    tokens = cleaned.split()
    if not tokens:
        return True

    greetings = {
        "hi", "hello", "hey", "namaste", "namaskar", "namaskaram",
        "pranam", "pranaam", "greetings", "good morning", "good afternoon", "good evening",
        "howdy", "hola", "thanks", "thank you", "dhanyavada", "dhanyavaad", "bye", "goodbye",
        "idk", "dont know", "dontknow", "dunno", "hmm", "ok", "okay", "k", "cool",
        "sup", "yo", "test", "testing", "what is this", "who are you", "what can you do"
    }

    joined = " ".join(tokens)
    if joined in greetings or raw in greetings or cleaned in greetings or collapsed in greetings:
        return True

    if any(tok in {"hi", "hello", "hey", "namaste", "namaskar", "pranam", "greetings", "idk"} for tok in tokens):
        domain_keywords = {"shloka", "sloka", "verse", "vata", "vayu", "pitta", "kapha", "nidana", "sushruta", "meaning", "explain", "chapter", "dhatu", "pada", "anvaya"}
        if not any(w in domain_keywords for w in tokens):
            return True

    if len(tokens) == 1 and tokens[0] in {"idk", "hmm", "ok", "cool", "fine", "yes", "no", "nope", "yep", "sure"}:
        return True

    return False

@app.post("/api/chat", response_model=ChatResponse)
def grounded_chat(req: ChatRequest):
    """
    RAG-grounded conversational assistant.
    Retrieves classical context strictly for the active shloka and user message,
    and returns a strictly grounded response with source citations.
    Greetings and small talk bypass retrieval and return zero source cards.
    Zero cross-shloka contamination: only chunks belonging to the active shloka are retrieved.
    """
    current_shloka = find_shloka(req.shloka_id)
    if not current_shloka:
        raise HTTPException(status_code=404, detail=f"Shloka '{req.shloka_id}' not found.")

    # 1. Greetings / small talk: bypass RAG retrieval completely and return no source cards
    if is_small_talk_or_greeting(req.message):
        system_instruction = (
            "You are a welcoming study assistant for Sushruta Samhita Nidana Sthana. "
            "The user is offering a greeting, casual remark, or small talk. "
            "Respond politely and briefly (1-2 sentences) in Sanskrit/English. "
            "Offer assistance with the study of the selected shloka, and do not perform medical analysis."
        )
        prompt = f"User message: {req.message}"
        llm = LLMClient()
        answer = llm.generate(prompt=prompt, system_prompt=system_instruction)
        return ChatResponse(
            response=answer,
            sources=[],
            shloka_id=req.shloka_id
        )

    # 2. Study questions: retrieve strictly for the active selected shloka (ZERO cross-shloka contamination)
    retriever = get_retriever_instance()

    # Query strictly filtered to current_shloka.id
    retrieved_chunks = retriever.retrieve(
        query=req.message,
        top_k=4,
        where_filter={"shloka_id": current_shloka.id}
    )

    # Fallback to shloka_number filter if shloka_id returned empty
    if not retrieved_chunks and current_shloka.shloka_number:
        retrieved_chunks = retriever.retrieve(
            query=req.message,
            top_k=4,
            where_filter={"shloka_number": current_shloka.shloka_number}
        )

    # Ensure no chunk from an unrelated shloka is included
    allowed_chunks = []
    for c in retrieved_chunks:
        c_sid = c.metadata.get("shloka_id") if c.metadata else None
        if (
            c_sid == current_shloka.id
            or str(c.shloka_number) == str(current_shloka.shloka_number)
            or (c.chunk_id and c.chunk_id.startswith(current_shloka.id))
        ):
            allowed_chunks.append(c)

    context_parts = []
    sources = []
    for r in allowed_chunks:
        ref_label = f"Śloka {r.shloka_number}" if r.shloka_number else "Ayurvidya Methodology"
        context_parts.append(f"[{r.source} - {ref_label} ({r.content_type})]:\n{r.text}")
        sources.append({
            "source": r.source,
            "shloka_number": r.shloka_number,
            "content_type": r.content_type,
            "similarity_score": r.similarity_score,
            "excerpt": r.text[:140] + "..." if len(r.text) > 140 else r.text
        })

    context_block = "\n\n".join(context_parts) if context_parts else "No specific context retrieved."

    system_instruction = (
        "You are a study assistant for the supplied Sushruta Samhita corpus.\n"
        "Answer the user's question using ONLY the retrieved context.\n"
        "If the retrieved context does not contain enough information, explicitly say that the supplied context does not provide enough information.\n"
        "Do not invent Sanskrit meanings, medical claims, or details.\n"
        "For greetings/small talk, respond naturally and briefly rather than forcing an Ayurveda answer."
    )

    prompt = (
        f"SELECTED SHLOKA:\n{current_shloka.text}\n\n"
        f"RETRIEVED CONTEXT:\n{context_block}\n\n"
        f"USER QUESTION:\n{req.message}"
    )

    llm = LLMClient()
    answer = llm.generate(prompt=prompt, system_prompt=system_instruction)

    # Temporary DEBUG logging (showing ONLY required fields, NEVER logging API key)
    retrieved_chunk_ids = [r.chunk_id for r in retrieved_chunks]
    gemini_called = (not llm.is_mock) and (llm.provider == "gemini")
    print(
        f"[CHAT DEBUG LOG] user_question={req.message!r} | "
        f"selected_shloka_id={current_shloka.id} | "
        f"retrieved_chunk_ids={retrieved_chunk_ids} | "
        f"provider={llm.provider} | model={llm.model} | "
        f"is_mock={llm.is_mock} | gemini_called={gemini_called}"
    )

    return ChatResponse(
        response=answer,
        sources=sources,
        shloka_id=req.shloka_id
    )

# ─────────────────────────────────────────────────────────────────────────────
# Static Frontend Files Mount & Root Route
# ─────────────────────────────────────────────────────────────────────────────
static_dir = project_root / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    """Serve the primary HTML application interface."""
    index_path = static_dir / "index.html"
    if not index_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "static/index.html not found. Please build frontend files."}
        )
    return FileResponse(
        str(index_path),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"}
    )

def start():
    """Entry point for running with uvicorn via CLI."""
    import uvicorn
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    start()
