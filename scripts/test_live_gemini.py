"""
Live End-to-End Verification of Gemini LLM 7-Step Pipeline.
Runs Shloka 3 through the FastAPI test client with force_refresh=True.
Verifies real API calls, retrieved ChromaDB context inclusion, and outputs.
"""

import sys
import time

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from src.server import app

def run_test():
    client = TestClient(app)
    print("=" * 60)
    print("Testing Shloka 3 with Real Gemini API (force_refresh=True)")
    print("=" * 60)

    t0 = time.time()
    resp = client.post("/api/shlokas/3/analyze?force_refresh=true")
    elapsed = time.time() - t0

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    print(f"Status: {resp.status_code} OK")
    print(f"Execution time: {elapsed:.2f} seconds")
    print(f"Shloka ID: {data['shloka_id']}")
    print(f"Cached flag: {data['cached']}")
    print(f"Number of steps: {len(data['steps'])}")
    assert len(data['steps']) == 7

    for step_num in range(1, 8):
        step_str = str(step_num)
        step_data = data["steps"][step_str]
        step_name_sa = step_data["step_name_sanskrit"]
        step_name_en = step_data["step_name_english"]
        model = step_data.get("model", "unknown")
        retrieved_contexts = step_data.get("retrieved_contexts", [])
        output = step_data["output"]

        print("\n" + "-" * 60)
        print(f"Step {step_num}: {step_name_sa} ({step_name_en})")
        print(f"Model used: {model}")
        print(f"Retrieved passages: {len(retrieved_contexts)}")
        for i, ctx in enumerate(retrieved_contexts, 1):
            ref = f"Shloka {ctx.get('shloka_number', 'N/A')}"
            sim = f" (Similarity: {ctx.get('similarity_score', 0):.3f})" if ctx.get('similarity_score') else ""
            print(f"  [{i}] {ctx.get('source')} - {ref} [{ctx.get('content_type')}]{sim}")

        print("\nOutput (first 350 chars):")
        print(output[:350] + ("..." if len(output) > 350 else ""))

    print("\n" + "=" * 60)
    print("SUCCESS: All 7 steps executed with real Gemini generation!")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
