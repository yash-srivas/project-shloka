"""
Unit Tests for Shloka Chunking and Data Loader.
Verifies shloka boundaries, metadata integrity, and schema compliance.
"""

import pytest
from src.chunker import build_and_save_processed_data
from src.schemas import ShlokaData, ChunkData

def test_shloka_loading_and_chunking():
    """Verify that shlokas and chunks are generated correctly with proper metadata."""
    shlokas, chunks = build_and_save_processed_data()

    assert len(shlokas) >= 5, "Expected at least 5 curated shlokas from Chapter 1"
    assert len(chunks) >= 15, "Expected granular chunks for verses, grammar, and methodology"

    # Test Shloka 1 structure
    shloka_1 = shlokas[0]
    assert shloka_1.shloka_number == 1
    assert "अथातो वातव्याधिदानं" in shloka_1.text
    assert shloka_1.sthana == "Nidana Sthana"
    assert shloka_1.chapter == "Vatavyadhi Nidana"

    # Test chunk metadata fields
    for chunk in chunks:
        assert chunk.id is not None and len(chunk.id) > 0
        assert chunk.text is not None and len(chunk.text.strip()) > 0
        assert "content_type" in chunk.metadata
        assert "source" in chunk.metadata
        assert chunk.metadata["content_type"] in ["shloka", "commentary", "grammar", "methodology"]

def test_methodology_chunks_presence():
    """Verify that Ayurvidya 7-step methodology chunks are included."""
    _, chunks = build_and_save_processed_data()
    methodology_chunks = [c for c in chunks if c.metadata.get("content_type") == "methodology"]
    
    assert len(methodology_chunks) >= 5, "Expected methodology chunks covering the 7 steps"
    step_topics = [c.metadata.get("category") for c in methodology_chunks]
    assert any("step1" in s for s in step_topics)
    assert any("step2" in s for s in step_topics)
    assert any("step3" in s for s in step_topics)
