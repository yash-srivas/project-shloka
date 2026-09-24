# Project Shloka: Sanskrit & Ayurveda Analysis RAG System
**Suśruta Saṃhitā · Nidāna Sthāna · Chapter 1: Vātavyādhi Nidāna**  
*Implementation of the 7-Stage Ayurvidya (Prabhāṣaṇam) Philological Methodology*

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vector DB](https://img.shields.io/badge/ChromaDB-0.5+-orange.svg)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-20%20passed-brightgreen.svg)](tests/)

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement & Objective](#problem-statement--objective)
3. [The 7-Step Prabhashanam Methodology](#the-7-step-prabhashanam-methodology)
4. [RAG System Architecture](#rag-system-architecture)
5. [Technology Stack](#technology-stack)
6. [Project Structure](#project-structure)
7. [Setup & Installation](#setup--installation)
8. [Configuration & Environment Variables](#configuration--environment-variables)
9. [Running the Application](#running-the-application)
   - [Primary Web UI (FastAPI + Vanilla Web Client)](#1-primary-web-ui-fastapi--vanilla-web-client)
   - [CLI 7-Step Pipeline](#2-cli-7-step-pipeline)
   - [Data Ingestion & Embedding Generation](#3-data-ingestion--embedding-generation)
   - [Vector Retrieval Inspection](#4-vector-retrieval-inspection)
   - [Secondary Streamlit Interface](#5-secondary-streamlit-interface)
10. [Running Automated Tests](#running-automated-tests)
11. [REST API Reference](#rest-api-reference)
12. [Known Limitations](#known-limitations)
13. [License & Acknowledgments](#license--acknowledgments)

---

## Project Overview

**Project Shloka** is a production-ready, domain-specialized **Retrieval-Augmented Generation (RAG)** application engineered for classical Sanskrit medical literature. It applies the rigorous classical 7-step **Ayurvidya / Prabhāṣaṇam** pedagogical method to verses from the *Suśruta Saṃhitā, Nidāna Sthāna, Adhyāya 1 (Vātavyādhi Nidāna)*.

By combining structured Sanskrit boundary-aware chunking, dense multilingual embeddings, ChromaDB vector storage, and grounded generative LLM orchestration (Google Gemini 2.5 Flash, OpenAI, Groq, or an Offline Grounded Mock), Project Shloka allows scholars, Ayurvedic practitioners, and students to unpack complex ślokas into granular grammatical, syntactic, lexical, and philosophical layers.

---

## Problem Statement & Objective

### The Challenge with Generic RAG on Sanskrit
Standard RAG frameworks split text mechanically every 500 or 1,000 characters. For Sanskrit ślokas, arbitrary character chunking destroys:
- **Metrical integrity (Chhandas)**: Verses are metrically organized (e.g., Anuṣṭubh: 4 padas of 8 syllables). Slicing midway breaks metrical coherence.
- **Sandhi and Samāsa (Compounds)**: Sanskrit joins words morphologically. Unaware chunking cuts compound terms in half, rendering them uninterpretable.
- **Syntactic relations (Anvaya)**: The Sanskrit prose order (*Anvaya*) rarely matches verse order (*Padya*). Preserving verse context alongside commentary is critical for proper reordering.
- **Contextual Grounding**: Generative LLMs hallucinate inaccurate etymologies (*Dhātu*, *Upasarga*) when not strictly grounded in classical commentaries (*Dalhana Nibandha Samgraha*, *Gayadasa Nyayachandrika*).

### Our Objective
1. **Preserve Sanskrit Verse Boundaries**: Keep every śloka intact alongside its syntax, morphology, and commentary chunks.
2. **Implement Authentic 7-Step Methodology**: Automate the Ayurvidya Prabhāṣaṇam 7-step analysis without hallucination.
3. **Strict Grounding & Traceability**: Ensure every stage cites retrieved classical passages with similarity metrics.
4. **Intelligent Conversational Assistance**: Provide an interactive verse-level tutor with automatic greeting/small-talk bypass (zero retrieval queries on greetings) and strict isolation to prevent cross-shloka contamination.

---

## The 7-Step Prabhashanam Methodology

The analytical engine executes the 7 steps codified in the supplied *Ayurvidya Prabhashanam* methodology (`data/raw/steps of Ayurvidya.pdf`):

| Step | Sanskrit Name | English Term | Analytical Focus |
|:---:|:---|:---|:---|
| **1** | **संप्रदानम्** | *Sampradānam* | Metrical division into 4 padas and progressive chanting combinations (1-word, 2-word, 3-word, 4-word progressive units). |
| **2** | **पदविभागः** | *Padavibhāga* | Word splitting and grammatical classification into सुबन्त (nouns), तिङन्त (verbs), and अव्यय (indeclinables), with sandhi separation. |
| **3** | **अन्वयः** | *Anvaya* | Syntactic reordering into standard Sanskrit grammatical sentence structure: कर्ता (Subject) → कर्म (Object) → क्रियापद (Verb). |
| **4** | **अन्वयार्थः** | *Anvayārtha* | Direct, word-by-word literal meaning strictly adhering to the *Anvaya* sentence order. |
| **5** | **भावार्थः** | *Bhāvārtha* | Concise contextual summary of the author's intended clinical purport and pathology (*Nidāna*). |
| **6** | **पदकृत्यम्** | *Padakṛtyam* | Morphological deep dive for key words: verbal roots (*Dhātu*), root meanings (*Dhātvartha*), prefixes (*Upasarga*), and compound analysis (*Samāsa Vigraha*). |
| **7** | **ध्वनितार्थः** | *Dhvanitārtha* | Implied, esoteric intent between the lines extracted via classical treatise canons (*Tantrayukti*). |

---

## RAG System Architecture

```
                       SOURCE DOCUMENTS (PDFs)
       data/raw/CHAPTER 1- VATAVYADHI NIDANA.pdf & steps of Ayurvidya.pdf
                                  ↓
                        DATA PREPARATION PIPELINE
                      src/data_loader.py + src/chunker.py
                                  ↓
                       STRUCTURED SHLOKA ARTIFACTS
                 data/processed/shlokas.json & chunks.json
                                  ↓
                         DENSE VECTOR EMBEDDINGS
             sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
                                  ↓
                        CHROMADB VECTOR STORAGE
                 storage/chroma/ (Persistent 384-dim index)
                                  ↓
                       STEP-AWARE VECTOR RETRIEVER
         src/retriever.py (Dynamic routing: grammar chunks for Steps 2/6,
                          commentary chunks for Steps 5/7)
                                  ↓
                       RAG-GROUNDED LLM ENGINE
         src/llm.py (Gemini 2.5 Flash / OpenAI / Groq / Offline Mock)
                                  ↓
                       7-STEP PIPELINE ORCHESTRATOR
                        prompts/ + src/pipeline.py
                                  ↓
                       HIGH-SPEED SQLITE CACHE
                   storage/cache.db (<0.05s response time)
                                  ↓
                         PRESENTATION LAYERS
           ┌──────────────────────────────────────────────┐
           │ FastAPI REST Server (src/server.py)          │
           │ ├── Modern Web UI (static/index.html, JS/CSS)│
           │ ├── Grounded Shloka Chatbot (/api/chat)      │
           │ └── Semantic Vector Search Modal (/api/search│
           └──────────────────────────────────────────────┘
           │ Streamlit Legacy UI (app/streamlit_app.py)   │
           │ CLI Batch Pipeline (scripts/run_pipeline.py) │
```

---

## Technology Stack

- **Core Backend**: Python 3.11+ / 3.12, [FastAPI](https://fastapi.tiangolo.com/), [Pydantic v2](https://docs.pydantic.dev/), Uvicorn
- **Vector Store**: [ChromaDB](https://www.trychroma.com/) (Persistent local SQLite-based vector store)
- **Embedding Models**: Hugging Face `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (with high-speed deterministic dense multilingual fallback)
- **LLM Orchestration**: Direct integration with Google Gemini 2.5 Flash (`google-genai` SDK), OpenAI, Groq, and an Offline Grounded Mock
- **Caching Layer**: SQLite3 (`storage/cache.db`) for instant sub-50ms reload of verified analyses
- **Frontend**: Vanilla HTML5, Vanilla CSS3 (Obsidian & Amber Manuscript theme), Modern ES6 JavaScript (Zero heavy frameworks, zero layout shifts)
- **Typography**: Google Fonts (`Tiro Devanagari Sanskrit`, `EB Garamond`, `Inter`, `JetBrains Mono`)
- **Automated Testing**: [Pytest](https://docs.pytest.org/), AnyIO, Starlette TestClient

---

## Project Structure

```
project-shloka/
│
├── data/
│   ├── raw/                           # Original source PDFs and reference documentation
│   │   ├── CHAPTER 1- VATAVYADHI NIDANA.pdf
│   │   ├── steps of Ayurvidya.pdf
│   │   ├── REAME.md                   # Supplied project task specifications
│   │   └── diagrams.md                # System flow diagrams
│   ├── processed/                     # Curated intermediate datasets
│   │   ├── shlokas.json               # Structured verse catalog
│   │   └── chunks.json                # Granular vector chunks with rich metadata
│   └── outputs/                       # Saved JSON analysis runs (.gitkeep tracked)
│
├── prompts/                           # 7 verified step prompt templates
│   ├── step1_sampradaanam.txt
│   ├── step2_padavibhaga.txt
│   ├── step3_anwaya.txt
│   ├── step4_anwayartha.txt
│   ├── step5_bhavartha.txt
│   ├── step6_padakrutyam.txt
│   └── step7_dhvanitartha.txt
│
├── src/                               # Core modular package
│   ├── __init__.py
│   ├── config.py                      # Dynamic configuration and paths
│   ├── schemas.py                     # Pydantic data contracts
│   ├── data_loader.py                 # PDF parser and shloka curator
│   ├── chunker.py                     # Shloka-boundary chunking logic
│   ├── embeddings.py                  # Multilingual dense embedding service
│   ├── vector_store.py                # ChromaDB collection interface
│   ├── retriever.py                   # Step-aware semantic retriever
│   ├── llm.py                         # Multi-provider LLM client with candidate fallback
│   ├── prompts.py                     # Prompt loader and template renderer
│   ├── pipeline.py                    # 7-step analysis orchestrator
│   ├── cache.py                       # SQLite cache manager
│   └── server.py                      # FastAPI REST API and static server
│
├── static/                            # Pure Vanilla Web Client
│   ├── index.html                     # Single-page application markup
│   ├── styles.css                     # Obsidian & Amber Manuscript stylesheet
│   └── app.js                         # Dynamic client application logic
│
├── app/
│   └── streamlit_app.py               # Secondary Streamlit demo interface
│
├── scripts/                           # Operational scripts and utilities
│   ├── ingest.py                      # Builds dataset and indexes ChromaDB
│   ├── run_pipeline.py                # CLI runner for 7-step analysis
│   ├── test_retrieval.py              # Tests semantic search queries
│   ├── evaluate_rag_and_shlokas.py    # Generates comprehensive RAG evaluation metrics
│   ├── audit_dataset.py               # Audits shlokas and chunks integrity
│   ├── test_live_gemini.py            # Verifies direct Gemini generation
│   ├── test_shloka_1_2.py             # Focused test for Śloka 1–2
│   ├── test_shloka_14_15.py           # Focused test for Śloka 14–15
│   ├── verify_prompts.py              # Validates step prompt files
│   ├── verify_retrieval_suite.py      # Verifies 21/21 retrieval windows
│   └── verify_source_pdf.py           # Validates PDF extraction
│
├── tests/                             # Automated test suite
│   ├── test_chunking.py               # Shloka boundaries and metadata tests
│   ├── test_gemini_llm.py             # LLM provider and fallback tests
│   ├── test_pipeline.py               # 7-step orchestrator & cache tests
│   ├── test_retrieval.py              # Vector search and filtering tests
│   └── test_server.py                 # FastAPI endpoints & chat tests
│
├── storage/                           # Persistent storage (ignored in Git via .gitkeep)
│   └── .gitkeep
│
├── .env.example                       # Environment template with safe defaults
├── .gitignore                         # Comprehensive Git exclusion rules
├── requirements.txt                   # Production dependencies
├── run.bat                            # Windows interactive terminal launcher
└── README.md                          # Project documentation (this file)
```

---

## Setup & Installation

### Prerequisites
- **Python 3.11** or **Python 3.12** installed
- Windows PowerShell, macOS Terminal, or Linux Bash
- Recommended: Git installed

### 1. Clone or Open the Repository
```bash
cd project-shloka
```

### 2. Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

---

## Configuration & Environment Variables

Create a `.env` file in the project root by copying the template:

```bash
cp .env.example .env
```

Edit `.env` to configure your preferred LLM provider:

```ini
# ===================================================
# Configuration for Sanskrit Shloka Analysis RAG System
# ===================================================

# Vector Database (ChromaDB)
CHROMA_COLLECTION_NAME=sushruta_vatavyadhi_chapter1
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# LLM Provider Configuration
# Supported providers: 'gemini', 'openai', 'groq', 'mock'
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash

# API Key (obtain from Google AI Studio: https://aistudio.google.com/)
LLM_API_KEY=your_actual_gemini_api_key_here
# GEMINI_API_KEY=your_actual_gemini_api_key_here  # Supported alias

# Retrieval Settings
DEFAULT_TOP_K=4

# Debug Mode (prints embeddings, retrieved docs, prompts, and LLM payloads)
DEBUG=false
```

> [!TIP]
> **Offline / No-Key Mode**: If you do not have an API key, set `LLM_PROVIDER=mock`. The application runs completely offline, synthesizing grounded answers directly from the retrieved classical context.

---

## Running the Application

### 1. Primary Web UI (FastAPI + Vanilla Web Client)
Start the high-performance FastAPI server:
```bash
python -m uvicorn src.server:app --host 127.0.0.1 --port 8000 --reload
```
Then open your browser to **`http://127.0.0.1:8000`**.

#### Features of the Primary Web Client:
- **Obsidian & Amber Manuscript Aesthetic**: Tailored dark theme featuring authentic Devanagari typography (`Tiro Devanagari Sanskrit`).
- **Sidebar Verse Navigator**: Quick dropdown and card list covering all Chapter 1 verses.
- **Dual View Modes**:
  - `📑 Single Step`: Tabbed view highlighting individual steps (`1. संप्रदानम्` through `7. ध्वनितार्थः`).
  - `📜 All 7 Steps`: Expandable/collapsible accordion layout presenting all 7 stages simultaneously with Expand All / Collapse All controls.
- **RAG Context Drawer**: Inspect the exact classical passages, content types, and cosine scores supporting each stage.
- **Grounded Chatbot**: Verse-specific study tutor that automatically bypasses RAG on greetings (`hi`, `hello`, `heyyyyyyyyyyyyyy`, `idk`) and isolates retrieval strictly to the active verse.
- **Semantic Search Modal (`/` shortcut)**: Search the entire ChromaDB corpus via keyboard shortcut.
- **State Synchronization**: Exact execution timing chips distinguishing fresh LLM runs from instant SQLite cache hits (`<0.05s`).

### 2. CLI 7-Step Pipeline
Run the 7-step analysis on any verse directly from your terminal:
```bash
# Analyze Śloka 1–2
python scripts/run_pipeline.py --shloka 1

# Analyze Śloka 13–14 (Prāṇa Vāyu) with forced cache refresh
python scripts/run_pipeline.py --shloka 13 --refresh
```

### 3. Data Ingestion & Embedding Generation
Extract verses from PDFs, build boundary-aware chunks, and index into ChromaDB:
```bash
python scripts/ingest.py
```

### 4. Vector Retrieval Inspection
Query the ChromaDB collection from the CLI:
```bash
python scripts/test_retrieval.py -q "प्राणो नाम देहधृक्"
python scripts/test_retrieval.py -q "Samana Vayu digestion"
```

### 5. Secondary Streamlit Interface
The project preserves the secondary Streamlit prototype:
```bash
streamlit run app/streamlit_app.py
```

### 6. Windows Launcher (`run.bat`)
On Windows, run the interactive launcher:
```bat
run.bat
```

---

## Running Automated Tests

The repository includes a comprehensive test suite covering chunking, embeddings, vector retrieval, LLM candidate fallback, the 7-step pipeline, SQLite caching, and FastAPI endpoints.

Run the test suite:
```bash
python -m pytest tests/ -v
```

### What the Tests Verify:
1. `tests/test_chunking.py`:
   - Validates that verse boundaries are preserved and not split midway.
   - Ensures methodology chunks (*Ayurvidya Prabhashanam*) are indexed with correct metadata.
2. `tests/test_gemini_llm.py`:
   - Validates Gemini provider initialization and API key parsing.
   - Verifies fallback to mock mode when no key is supplied.
   - Asserts that real API keys are never printed to stdout or logs.
   - Validates temperature and system instruction passing.
3. `tests/test_pipeline.py`:
   - Validates end-to-end execution of all 7 steps.
   - Measures per-step execution latencies across analytical stages.
   - Verifies that SQLite cache persists and reloads steps accurately.
4. `tests/test_retrieval.py`:
   - Validates ChromaDB collection document counts and embedding dimensions.
   - Verifies semantic cosine similarity and step-specific routing (grammar vs. commentary).
   - Validates confidence threshold filtering (`min_similarity`).
5. `tests/test_server.py`:
   - Validates FastAPI endpoints (`/api/status`, `/api/shlokas`, `/api/chat`, `/api/search`, `/api/shlokas/{id}/export`).
   - Verifies static index serving, chat grounding, and study dossier exports in Markdown and JSON formats.

---

## REST API Reference

The FastAPI server provides clean, documented JSON REST endpoints:

| HTTP Method | Route | Description |
|:---|:---|:---|
| `GET` | `/` | Serves the single-page HTML client (`static/index.html`) |
| `GET` | `/api/status` | Returns system health, indexed chunk count, active LLM provider, and model |
| `GET` | `/api/shlokas` | Returns the complete catalog of Chapter 1 verses with transliterations and titles |
| `GET` | `/api/shlokas/{shloka_id}` | Returns verse details and any pre-cached 7-step analysis outputs |
| `POST` | `/api/shlokas/{shloka_id}/analyze` | Triggers the 7-step pipeline (`?force_refresh=true` bypasses cache) |
| `GET` | `/api/shlokas/{shloka_id}/export?format={markdown\|json}` | Generates and exports downloadable philological analysis dossiers |
| `DELETE` | `/api/shlokas/{shloka_id}/cache` | Clears cached steps for the specified verse |
| `GET` | `/api/search?q={query}&top_k=4&min_similarity=0.3` | Performs cosine similarity search across ChromaDB with optional threshold |
| `POST` | `/api/chat` | Grounded conversational Q&A endpoint for the active verse |

---

## Known Limitations

1. **Chapter Scope**: The current dataset focuses on Chapter 1 of *Nidāna Sthāna* (*Vātavyādhi Nidāna*). Additional chapters of the *Suśruta Saṃhitā* can be added following the same chunking structure.
2. **LLM Quotas**: When using free-tier Google Gemini API keys, Google enforces per-minute rate limits. The client includes automatic candidate model fallback (`gemini-2.5-flash` → `gemini-flash-lite-latest` → `gemini-1.5-flash`) to mitigate rate limiting.
3. **Hardware Acceleration**: Embedding generation runs efficiently on standard CPU using the lightweight 384-dimensional MiniLM architecture. If PyTorch CUDA is installed, GPU acceleration is automatically leveraged.

---

## License & Acknowledgments

- **Classical Text**: *Suśruta Saṃhitā*, *Nidāna Sthāna*, Chapter 1 (*Vātavyādhi Nidāna*), based on traditional editions and commentary (*Dalhana Nibandha Samgraha*).
- **Methodology**: *Ayurvidya / Prabhāṣaṇam 7-Step Philological Method* (`steps of Ayurvidya.pdf`).
- **Code License**: MIT License. See `LICENSE` for details.
