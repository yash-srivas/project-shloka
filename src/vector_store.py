"""
Vector Store Module for Sanskrit Shloka Analysis RAG System.
Manages ChromaDB persistent vector database storage, indexing, and vector similarity search.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import CHROMA_DIR, CHROMA_COLLECTION_NAME, DEBUG_MODE
from src.schemas import ChunkData, RetrievalResult

class ChromaVectorStore:
    """Manages persistent ChromaDB vector storage and semantic querying."""

    def __init__(
        self,
        persist_directory: Path = CHROMA_DIR,
        collection_name: str = CHROMA_COLLECTION_NAME
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._initialize_chroma()

    def _initialize_chroma(self):
        """Initialize persistent ChromaDB client and collection."""
        import chromadb
        from chromadb.config import Settings

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Sushruta Samhita Vatavyadhi Nidana Chapter 1 and Ayurvidya Methodology"}
        )
        if DEBUG_MODE:
            print(f"[VectorStore] Initialized ChromaDB at {self.persist_directory} (Collection: {self.collection_name})")

    def count(self) -> int:
        """Return total number of indexed documents in collection."""
        return self.collection.count()

    def add_chunks(self, chunks: List[ChunkData], embeddings: List[List[float]]) -> int:
        """
        Add or update chunks with their corresponding embeddings in ChromaDB.
        Avoids duplicates by using chunk.id as unique identifier (upsert).
        """
        if not chunks:
            return 0

        ids = [c.id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]

        # Use upsert to handle idempotence safely
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return len(chunks)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 4,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Perform vector similarity search against ChromaDB collection.
        Returns sorted list of RetrievalResult objects.
        """
        count = self.count()
        if count == 0:
            return []

        n_results = min(top_k, count)
        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }

        if where_filter:
            query_kwargs["where"] = where_filter

        raw_results = self.collection.query(**query_kwargs)

        results: List[RetrievalResult] = []
        if not raw_results or not raw_results.get("ids") or not raw_results["ids"][0]:
            return results

        ids = raw_results["ids"][0]
        documents = raw_results["documents"][0]
        metadatas = raw_results["metadatas"][0]
        distances = raw_results["distances"][0] if "distances" in raw_results else [0.0] * len(ids)

        for chunk_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
            # Calculate cosine similarity score (chroma default cosine distance = 1 - cosine_similarity)
            # Distance 0 => similarity 1.0; distance 1 => similarity 0.0
            similarity = max(0.0, 1.0 - (dist / 2.0)) if dist is not None else None

            results.append(RetrievalResult(
                chunk_id=chunk_id,
                text=doc,
                metadata=meta or {},
                distance=round(dist, 4) if dist is not None else None,
                similarity_score=round(similarity, 4) if similarity is not None else None,
                source=meta.get("source", "Sushruta Samhita") if meta else "Sushruta Samhita",
                shloka_number=meta.get("shloka_number") if meta else None,
                content_type=meta.get("content_type", "shloka") if meta else "shloka"
            ))

        return results

    def clear(self):
        """Empty the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(name=self.collection_name)
