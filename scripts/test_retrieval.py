"""
Retrieval Test Script for Sanskrit Shloka Analysis RAG System.
Allows mentors and students to verify semantic search and inspect retrieved chunks.
"""

import sys
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal when printing Devanagari
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in pythonpath
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.retriever import ShlokaRetriever
from src.vector_store import ChromaVectorStore

def format_result(index: int, res) -> str:
    shloka_display = f"Shloka {res.shloka_number}" if res.shloka_number else "Methodology"
    score_display = f"{res.similarity_score:.4f}" if res.similarity_score is not None else "N/A"
    dist_display = f"{res.distance:.4f}" if res.distance is not None else "N/A"

    lines = [
        f"RESULT {index}",
        "-" * 40,
        f"Source:      {res.source}",
        f"Chapter:     {res.metadata.get('chapter', 'N/A')}",
        f"Shloka:      {shloka_display}",
        f"Type:        {res.content_type} ({res.metadata.get('category', 'general')})",
        f"Sim Score:   {score_display} (Distance: {dist_display})",
        f"Text:\n{res.text.strip()}",
        "-" * 40
    ]
    return "\n".join(lines)

def run_retrieval_test(query: str, top_k: int = 4):
    print("=" * 60)
    print(f"Testing Semantic Retrieval for Query:\n'{query}'")
    print("=" * 60)

    store = ChromaVectorStore()
    total_docs = store.count()
    if total_docs == 0:
        print("\n[Warning] The ChromaDB collection is empty! Please run 'python scripts/ingest.py' first.")
        return

    retriever = ShlokaRetriever(vector_store=store)
    results = retriever.retrieve(query=query, top_k=top_k)

    if not results:
        print("\nNo relevant documents retrieved.")
        return

    print(f"\nRetrieved {len(results)} relevant chunks (Top-{top_k}):\n")
    for idx, r in enumerate(results, 1):
        print(format_result(idx, r))
        print()

def main():
    parser = argparse.ArgumentParser(description="Test Sanskrit Semantic Retrieval in ChromaDB.")
    parser.add_argument("--query", "-q", type=str, default=None, help="Query string to search for.")
    parser.add_argument("--top_k", "-k", type=int, default=3, help="Number of results to return.")
    args = parser.parse_args()

    if args.query:
        run_retrieval_test(args.query, top_k=args.top_k)
    else:
        default_query = "What is the function and pathology of Prana Vayu?"
        print(f"No query specified. Running default demonstration query: '{default_query}'\n")
        run_retrieval_test(default_query, top_k=args.top_k)

        print("\n--- Additional Test Queries you can try ---")
        print("1. python scripts/test_retrieval.py -q \"स्वयम्भूरेष भगवान् वायुः\"")
        print("2. python scripts/test_retrieval.py -q \"How does Samana Vayu digest food?\"")
        print("3. python scripts/test_retrieval.py -q \"समानो वह्निंसङ्गतः\"")

if __name__ == "__main__":
    main()
