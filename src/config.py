"""
Configuration Module for Sanskrit Shloka Analysis RAG System.
Handles environment variables, paths, and model settings.
"""

import sys
import os

# Reconfigure stdout and stderr for Unicode (Devanagari) on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from pathlib import Path
from dotenv import load_dotenv

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = DATA_DIR / "outputs"
STORAGE_DIR = PROJECT_ROOT / "storage"
CHROMA_DIR = STORAGE_DIR / "chroma"
CACHE_DB_PATH = STORAGE_DIR / "cache.db"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# Ensure runtime directories exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env with override=True
load_dotenv(PROJECT_ROOT / ".env", override=True)

def get_active_llm_config() -> tuple:
    """Dynamically read current LLM provider, model, and api key from .env."""
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    default_model = "gemini-2.5-flash" if provider == "gemini" else "gpt-4o-mini"
    model = os.getenv("LLM_MODEL", default_model)
    api_key = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    return provider, model, api_key

# Vector Database Config
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "sushruta_vatavyadhi_chapter1")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# LLM Configuration
# Supported providers: 'openai', 'gemini', 'anthropic', 'groq', 'mock'
LLM_PROVIDER, LLM_MODEL, LLM_API_KEY = get_active_llm_config()

# Retrieval Settings
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "4"))

# Debug Mode
DEBUG_MODE = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

def get_config_summary() -> dict:
    """Return dictionary of current configuration settings for display or debug."""
    provider, model, api_key = get_active_llm_config()
    return {
        "project_root": str(PROJECT_ROOT),
        "chroma_dir": str(CHROMA_DIR),
        "collection_name": os.getenv("CHROMA_COLLECTION_NAME", CHROMA_COLLECTION_NAME),
        "embedding_model": os.getenv("EMBEDDING_MODEL_NAME", EMBEDDING_MODEL_NAME),
        "llm_provider": provider,
        "llm_model": model,
        "has_api_key": bool(api_key and api_key.strip() != ""),
        "debug_mode": os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    }

