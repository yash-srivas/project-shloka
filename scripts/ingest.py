"""
Ingestion Script for Sanskrit Shloka Analysis RAG System.
Executes:
1. Data preparation and shloka-boundary chunking
2. Saving processed datasets to data/processed/
3. Dense vector embedding generation
4. Persistent ChromaDB insertion (upsert to prevent duplicates)
5. Statistical validation report
"""

import sys
from pathlib import Path

# Ensure project root is in pythonpath
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import PROCESSED_DATA_DIR, CHROMA_COLLECTION_NAME
from src.chunker import build_and_save_processed_data
from src.embeddings import EmbeddingService
from src.vector_store import ChromaVectorStore

def run_ingestion():
    print("=" * 60)
    print("Starting Sanskrit Shloka & Commentary Ingestion Pipeline")
    print("=" * 60)

    # 1. Prepare and save data
    print("\n[Step 1/3] Processing source documents and building shloka-based chunks...")
    shlokas, chunks = build_and_save_processed_data()
    print(f"-> Successfully loaded {len(shlokas)} shloka records.")
    print(f"-> Generated {len(chunks)} contextual chunks.")

    # 2. Generate embeddings
    print(f"\n[Step 2/3] Generating dense embeddings for {len(chunks)} chunks...")
    embedding_service = EmbeddingService()
    texts = [c.text for c in chunks]
    embeddings = embedding_service.embed_documents(texts)
    print(f"-> Generated {len(embeddings)} vectors (dimension: {embedding_service.embedding_dimension}).")

    # 3. Store in ChromaDB
    print(f"\n[Step 3/3] Storing embeddings and metadata in ChromaDB ({CHROMA_COLLECTION_NAME})...")
    vector_store = ChromaVectorStore()
    added_count = vector_store.add_chunks(chunks, embeddings)
    total_docs = vector_store.count()

    print("\n" + "=" * 60)
    print("Ingestion Summary")
    print("=" * 60)
    print(f"Documents loaded:    {len(shlokas)}")
    print(f"Chunks created:      {len(chunks)}")
    print(f"Embeddings generated:{len(embeddings)}")
    print(f"Chroma documents:    {total_docs}")
    print("Ingestion complete.")
    print("=" * 60)

if __name__ == "__main__":
    run_ingestion()
