import sys
from pathlib import Path

# Ensure project root is in pythonpath
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.retriever import ShlokaRetriever
from src.vector_store import ChromaVectorStore

test_queries = [
    # Query 1: Mangalacharana and Dhanvantari
    "अथातो वातव्याधिदानं व्याख्यास्यामः",
    # Query 2: Cosmic and divine nature of Vayu (Svayambhu)
    "स्वातन्त्र्यान्नित्यभावाच्च सर्वगत्वात्तथैव च",
    # Query 3: Prana Vayu location and pathology (hiccups, asthma)
    "यो वायुर्वक्त्रसञ्चारी प्राणः हिक्का श्वास",
    # Query 4: Samana Vayu, digestive fire, and separation of nutrients/waste
    "समानो वह्निंसङ्गतः अन्नं पचति",
    # Query 5: Methodological rules of Padavibhaga and Samasa preservation
    "How to classify subanta, tinganta, and avyaya without splitting samasa?"
]

store = ChromaVectorStore()
retriever = ShlokaRetriever(vector_store=store)

print("=" * 80)
print("RUNNING 5-QUERY RETRIEVAL VERIFICATION SUITE")
print("=" * 80)

for idx, q in enumerate(test_queries, 1):
    print(f"\nQUERY {idx}: \"{q}\"")
    print("-" * 80)
    results = retriever.retrieve(query=q, top_k=2)
    for r_idx, r in enumerate(results, 1):
        shloka_lbl = f"Shloka #{r.shloka_number}" if r.shloka_number else "Methodology"
        sim_score = f"{r.similarity_score:.4f}" if r.similarity_score is not None else "N/A"
        dist = f"{r.distance:.4f}" if r.distance is not None else "N/A"
        first_line = r.text.splitlines()[0] if r.text else ""
        print(f"  Result {r_idx}: [{r.source} | {shloka_lbl} | Type: {r.content_type}] (Score: {sim_score}, Dist: {dist})")
        print(f"            Preview: \"{first_line[:90]}...\"")
print("\n" + "=" * 80)
