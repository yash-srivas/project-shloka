"""
Evaluation script for 3 representative shlokas:
- Śloka 1–2 (Invocation & Authority)
- Śloka 3–4 (Questions of Sushruta to Dhanvantari)
- Śloka 14–15 (Udana Vayu functions and pathology)

Runs fresh 7-step analysis, inspects outputs, and gathers detailed RAG retrieval metrics.
"""

import urllib.request
import json
import time
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.retriever import ShlokaRetriever
from src.chunker import build_and_save_processed_data

def evaluate():
    shlokas, _ = build_and_save_processed_data()
    target_shlokas = [
        next(s for s in shlokas if s.shloka_number == 1),
        next(s for s in shlokas if s.shloka_number == 3),
        next(s for s in shlokas if s.shloka_number == 14)
    ]

    retriever = ShlokaRetriever()
    results_summary = []

    for s in target_shlokas:
        display_num = s.shloka_number_display
        shloka_id = s.id
        print(f"\n=======================================================")
        print(f"EVALUATING ŚLOKA {display_num} ({shloka_id})")
        print(f"=======================================================")
        
        # 1. Clear cache
        del_req = urllib.request.Request(f"http://127.0.0.1:8000/api/shlokas/{s.shloka_number}/cache", method="DELETE")
        try:
            with urllib.request.urlopen(del_req) as resp:
                pass
            print(f"[Cache] Cleared cache for Śloka {display_num}")
        except Exception as e:
            print(f"[Cache Warning] {e}")

        # 2. Run fresh analysis
        print(f"[API] Running fresh 7-step analysis via POST /api/shlokas/{s.shloka_number}/analyze?force_refresh=true...")
        t0 = time.time()
        analyze_req = urllib.request.Request(f"http://127.0.0.1:8000/api/shlokas/{s.shloka_number}/analyze?force_refresh=true", method="POST")
        with urllib.request.urlopen(analyze_req, timeout=180) as resp:
            analysis_data = json.loads(resp.read().decode("utf-8"))
        elapsed = time.time() - t0
        print(f"[API] Completed in {elapsed:.2f}s (reported: {analysis_data.get('execution_time_seconds')}s)")

        # 3. Collect retrieval evaluation for all 7 steps
        shloka_eval = {
            "shloka_id": shloka_id,
            "shloka_number_display": display_num,
            "shloka_text": s.text,
            "elapsed_seconds": elapsed,
            "steps": {}
        }

        # Detailed step query templates
        step_queries = {
            1: f"संप्रदानम् पादविभाग पद्यसूत्र छन्दस् {s.text}",
            2: f"सुबन्त तिङन्त अव्यय सन्धि समास पदविभाग {s.text}",
            3: f"अन्वयः कारक विभक्ति कर्तृ कर्म क्रिया अन्वयवाक्यम् {s.text}",
            4: f"अन्वयार्थ शब्दार्थ literal meaning {s.text}",
            5: f"भावार्थः सुश्रुत वातव्याधि निदान सन्दर्भ प्रयोजन {s.text}",
            6: f"पदकृत्यम् धातु धात्वर्थ उपसर्ग समास विग्रह अमरकोश {s.text}",
            7: f"ध्वनितार्थः तन्त्रयुक्ति तन्त्रसमन्वय चरक सुश्रुत गूढार्थ {s.text}"
        }

        steps_payload = analysis_data.get("steps", {})

        for step_num in range(1, 8):
            step_key = str(step_num)
            step_data = steps_payload.get(step_key, {})
            output_text = step_data.get("output", "")
            retrieved_raw = step_data.get("retrieved_contexts", [])

            # Get exact query and retrieved metadata
            query_used = step_queries[step_num]
            retrieved_info = []
            for r in retrieved_raw:
                retrieved_info.append({
                    "chunk_id": r.get("chunk_id"),
                    "content_type": r.get("content_type"),
                    "category": r.get("category"),
                    "shloka_number": r.get("shloka_number"),
                    "similarity_score": r.get("similarity_score"),
                    "text_preview": r.get("text", "")[:120].replace("\n", " ")
                })

            shloka_eval["steps"][step_num] = {
                "step_name_sa": step_data.get("step_name_sanskrit", ""),
                "step_name_en": step_data.get("step_name_english", ""),
                "query": query_used,
                "retrieved_chunks": retrieved_info,
                "output_preview": output_text[:300].replace("\n", " ") + "...",
                "full_output": output_text
            }

        results_summary.append(shloka_eval)

    # Save full evaluation data to JSON
    out_file = Path("storage/rag_evaluation_report.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(results_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[Saved] Full evaluation report written to {out_file}")

if __name__ == "__main__":
    evaluate()
