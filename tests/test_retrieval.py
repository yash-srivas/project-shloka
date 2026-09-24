"""
Unit Tests for Vector DB Indexing and Semantic Retrieval.
Verifies ChromaDB collection operations, embedding generation, and search precision.
"""

import pytest
from src.chunker import build_and_save_processed_data
from src.embeddings import EmbeddingService
from src.vector_store import ChromaVectorStore
from src.retriever import ShlokaRetriever

@pytest.fixture(scope="module")
def setup_vector_store():
    """Ensure vector database is populated for testing."""
    shlokas, chunks = build_and_save_processed_data()
    embedder = EmbeddingService()
    vector_store = ChromaVectorStore()
    
    # Generate embeddings and upsert
    texts = [c.text for c in chunks]
    embeddings = embedder.embed_documents(texts)
    vector_store.add_chunks(chunks, embeddings)
    
    return vector_store, embedder

def test_vector_store_count(setup_vector_store):
    """Verify that chunks are indexed in ChromaDB."""
    vector_store, _ = setup_vector_store
    count = vector_store.count()
    assert count > 0, "ChromaDB should contain indexed chunks"

def test_semantic_retrieval_query(setup_vector_store):
    """Verify that semantic queries retrieve relevant shlokas."""
    vector_store, embedder = setup_vector_store
    retriever = ShlokaRetriever(vector_store=vector_store, embedding_service=embedder)

    results = retriever.retrieve("What is Prana Vayu and where does it circulate?", top_k=3)
    assert len(results) > 0, "Retrieval should return results for a valid query"
    
    top_result = results[0]
    assert top_result.chunk_id is not None
    assert top_result.text is not None and len(top_result.text) > 0
    assert top_result.source == "Sushruta Samhita" or "Ayurvidya" in top_result.source

def test_step_specific_retrieval(setup_vector_store):
    """Verify that step-specific retrieval returns appropriate content types."""
    vector_store, embedder = setup_vector_store
    retriever = ShlokaRetriever(vector_store=vector_store, embedding_service=embedder)

    # Step 2: Padavibhaga (expects grammar or shloka content)
    grammar_results = retriever.retrieve_for_step(step_number=2, shloka_text="अथातो वातव्याधिदानं व्याख्यास्यामः", top_k=3)
    assert len(grammar_results) > 0
    types = [r.content_type for r in grammar_results]
    assert any(t in ["grammar", "shloka", "methodology"] for t in types)

def test_similarity_threshold_filtering(setup_vector_store):
    """Verify that min_similarity filters out results below the score cutoff."""
    vector_store, embedder = setup_vector_store
    retriever = ShlokaRetriever(vector_store=vector_store, embedding_service=embedder)

    unfiltered = retriever.retrieve("Vata dosha symptoms", top_k=5)
    assert len(unfiltered) > 0

    # With a reasonable threshold (0.2), results should be returned with scores >= 0.2
    filtered = retriever.retrieve("Vata dosha symptoms", top_k=5, min_similarity=0.2)
    for item in filtered:
        assert item.similarity_score >= 0.2

    # With an impossible threshold (0.999), results should be empty
    impossible = retriever.retrieve_with_threshold("Vata dosha symptoms", min_similarity=0.999, top_k=5)
    assert len(impossible) == 0

