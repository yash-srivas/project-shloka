"""
Pydantic Schemas for Sanskrit Shloka Analysis RAG System.
Ensures strong typing, serialization, and clean API boundaries.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ShlokaData(BaseModel):
    """Represents a primary Sanskrit verse (Shloka) with reference info."""
    id: str = Field(..., description="Unique identifier e.g. sushruta_ch1_shloka_001")
    source: str = Field(default="Sushruta Samhita")
    sthana: str = Field(default="Nidana Sthana")
    chapter: str = Field(default="Vatavyadhi Nidana")
    chapter_number: int = Field(default=1)
    shloka_number: int = Field(..., description="Shloka number within chapter")
    shloka_number_display: str = Field(..., description="Display string e.g. '1', '1-2', '3-4'")
    text: str = Field(..., description="Original Sanskrit shloka text in Devanagari")
    transliteration: Optional[str] = Field(default=None, description="IAST transliteration if available")
    english_title: Optional[str] = Field(default=None, description="Short summary/topic")
    associated_pages: List[int] = Field(default_factory=list, description="Pages in source document")

class ChunkMetadata(BaseModel):
    """Metadata attached to each vector embedding chunk."""
    source: str = "Sushruta Samhita"
    sthana: str = "Nidana Sthana"
    chapter: str = "Vatavyadhi Nidana"
    shloka_number: Optional[int] = None
    shloka_id: Optional[str] = None
    content_type: str = Field(..., description="'shloka', 'commentary', 'grammar', 'methodology'")
    category: Optional[str] = Field(default="general", description="Subcategory: e.g. 'sandhi', 'samasa', 'dhatu', 'bhavartha'")
    language: str = "Sanskrit"
    page_number: Optional[int] = None

class ChunkData(BaseModel):
    """A single chunk ready for vector database indexing."""
    id: str
    text: str
    metadata: Dict[str, Any]

class RetrievalResult(BaseModel):
    """A retrieved chunk from vector search with similarity metric."""
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None
    similarity_score: Optional[float] = None
    source: str = "Sushruta Samhita"
    shloka_number: Optional[int] = None
    content_type: str = "shloka"

class StepOutput(BaseModel):
    """Output from an individual pipeline step."""
    step_number: int
    step_name_sanskrit: str
    step_name_english: str
    output: str
    retrieved_contexts: List[RetrievalResult] = Field(default_factory=list)
    model: str = "default"
    latency_seconds: Optional[float] = Field(default=None, description="Execution time for this step in seconds")

class PipelineResult(BaseModel):
    """Aggregated output of all 7 analysis steps for a shloka."""
    shloka_id: str
    shloka_number: int
    shloka_text: str
    steps: Dict[int, StepOutput] = Field(default_factory=dict)
    execution_time_seconds: float = 0.0
    step_latencies: Dict[int, float] = Field(default_factory=dict, description="Execution latency breakdown per step")
    cached: bool = False
    timestamp: Optional[str] = None

class ChatMessage(BaseModel):
    """Chat message for conversational Q&A grounded in shloka context."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    shloka_id: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
