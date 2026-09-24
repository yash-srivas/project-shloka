"""
Retriever Module for Sanskrit Shloka Analysis RAG System.
Provides standard semantic vector retrieval as well as step-specific retrieval
aware of the grammatical, morphological, and philosophical targets of each step.
"""

from typing import List, Optional, Dict, Any
from src.embeddings import EmbeddingService
from src.vector_store import ChromaVectorStore
from src.schemas import RetrievalResult
from src.config import DEFAULT_TOP_K, DEBUG_MODE

class ShlokaRetriever:
    """Semantic retriever connecting queries to ChromaDB vector store."""

    def __init__(
        self,
        vector_store: Optional[ChromaVectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        self.vector_store = vector_store or ChromaVectorStore()
        self.embedding_service = embedding_service or EmbeddingService()

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        where_filter: Optional[Dict[str, Any]] = None,
        min_similarity: Optional[float] = None
    ) -> List[RetrievalResult]:
        """
        General semantic retrieval for a user or system query.
        Returns top-k most relevant chunks with distance and metadata.
        Optionally filters results below min_similarity threshold.
        """
        if DEBUG_MODE:
            print(f"[Retriever] Query: '{query[:80]}...' (top_k={top_k}, filter={where_filter}, min_sim={min_similarity})")

        # 1. Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # 2. Vector search in ChromaDB
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            where_filter=where_filter
        )

        # 3. Apply optional similarity threshold filter
        if min_similarity is not None:
            results = [
                r for r in results
                if r.similarity_score is not None and r.similarity_score >= min_similarity
            ]

        if DEBUG_MODE:
            print(f"[Retriever] Retrieved {len(results)} chunks.")

        return results

    def retrieve_with_threshold(
        self,
        query: str,
        min_similarity: float = 0.5,
        top_k: int = DEFAULT_TOP_K,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Convenience method for semantic search strictly enforcing a confidence cutoff."""
        return self.retrieve(
            query=query,
            top_k=top_k,
            where_filter=where_filter,
            min_similarity=min_similarity
        )

    def retrieve_for_step(
        self,
        step_number: int,
        shloka_text: str,
        shloka_number: Optional[int] = None,
        top_k: int = 4,
        min_similarity: Optional[float] = None
    ) -> List[RetrievalResult]:
        """
        Step-aware retrieval tailored to the specific needs of each of the 7 steps:
        - Step 1: Chanting units & metrical division methodology
        - Step 2: Sanskrit grammar, padas, sandhi, samasa preservation
        - Step 3: Anwaya ordering rules & case relation syntax
        - Step 4: Literal word definitions and meaning
        - Step 5: Ayurvedic pathology, clinical context, Bhavartha
        - Step 6: Dhatu, dhatvartha, samasa vigraha, word formation
        - Step 7: Classical synthesis, Tantrayukti, deeper implied intent
        """
        # Formulate query text targeted to the step (put step keywords first for optimal embedding attention)
        step_queries = {
            1: f"संप्रदानम् पादविभाग पद्यसूत्र छन्दस् {shloka_text}",
            2: f"सुबन्त तिङन्त अव्यय सन्धि समास पदविभाग {shloka_text}",
            3: f"अन्वयः कारक विभक्ति कर्तृ कर्म क्रिया अन्वयवाक्यम् {shloka_text}",
            4: f"अन्वयार्थ शब्दार्थ literal meaning {shloka_text}",
            5: f"भावार्थः सुश्रुत वातव्याधि निदान सन्दर्भ प्रयोजन {shloka_text}",
            6: f"पदकृत्यम् धातु धात्वर्थ उपसर्ग समास विग्रह अमरकोश {shloka_text}",
            7: f"ध्वनितार्थः तन्त्रयुक्ति तन्त्रसमन्वय चरक सुश्रुत गूढार्थ {shloka_text}"
        }

        query = step_queries.get(step_number, shloka_text)

        # Primary attempt: target relevant content types if possible
        target_content_type = None
        if step_number in (2, 3):
            target_content_type = "grammar"
        elif step_number == 5:
            target_content_type = "commentary"
        elif step_number == 6:
            target_content_type = "grammar"
        elif step_number == 7:
            target_content_type = "commentary"

        where_filter = None
        if target_content_type:
            where_filter = {"content_type": target_content_type}

        results = self.retrieve(query=query, top_k=top_k, where_filter=where_filter, min_similarity=min_similarity)

        # If filtered search yielded fewer results than desired, backfill with general search
        if len(results) < top_k:
            general_results = self.retrieve(query=query, top_k=top_k, where_filter=None, min_similarity=min_similarity)
            seen_ids = {r.chunk_id for r in results}
            for gr in general_results:
                if gr.chunk_id not in seen_ids and len(results) < top_k:
                    results.append(gr)
                    seen_ids.add(gr.chunk_id)

        # If a specific shloka_number is provided, ensure that shloka's own chunks are represented at the top
        if shloka_number is not None:
            shloka_own = self.retrieve(
                query=query,
                top_k=top_k,
                where_filter={"shloka_number": shloka_number},
                min_similarity=min_similarity
            )
            shloka_own_ids = {so.chunk_id for so in shloka_own}
            results = shloka_own + [r for r in results if r.chunk_id not in shloka_own_ids]

        return results[:top_k]
