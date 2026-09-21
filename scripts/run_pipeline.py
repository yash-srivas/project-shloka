"""
CLI Runner for the 7-Step Sanskrit Shloka Analysis Pipeline.
Executes the full seven steps for a chosen Shloka (1 to 17), prints the results,
displays retrieved evidence, and optionally saves the structured JSON report.
"""

import sys
import json
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

from src.config import OUTPUTS_DIR
from src.chunker import build_and_save_processed_data
from src.pipeline import ShlokaPipelineOrchestrator
from src.prompts import STEPS_CONFIG

def main():
    parser = argparse.ArgumentParser(description="Run 7-Step Sanskrit Shloka Analysis Pipeline.")
    parser.add_argument("--shloka", "-s", type=int, default=1, help="Shloka number to analyze (e.g. 1, 3, 5, 9, 11, 12, 13, 14, 16).")
    parser.add_argument("--refresh", "-r", action="store_true", help="Force regenerate steps bypassing cache.")
    parser.add_argument("--save", action="store_true", default=True, help="Save generated output to data/outputs/")
    args = parser.parse_args()

    # Load shlokas data
    shlokas, _ = build_and_save_processed_data()
    target_shloka = None
    for s in shlokas:
        if s.shloka_number == args.shloka:
            target_shloka = s
            break

    if not target_shloka:
        print(f"[Error] Shloka #{args.shloka} not found. Available shlokas: {[s.shloka_number for s in shlokas]}")
        return

    print("=" * 70)
    print(f"AYURVIDYA / PRABHASHANAM 7-STEP SHLOKA ANALYSIS")
    print(f"Source: {target_shloka.source} - {target_shloka.sthana} - {target_shloka.chapter}")
    print(f"Shloka #{target_shloka.shloka_number_display}: {target_shloka.english_title or ''}")
    print("=" * 70)
    print(f"\n[ORIGINAL SANSKRIT SHLOKA]:\n{target_shloka.text}\n")
    print("=" * 70)

    orchestrator = ShlokaPipelineOrchestrator()
    result = orchestrator.run_analysis(shloka=target_shloka, force_refresh=args.refresh)

    for step_num in range(1, 8):
        step_meta = STEPS_CONFIG[step_num]
        step_res = result.steps.get(step_num)
        print("\n" + "#" * 60)
        print(f"STEP {step_num}: {step_meta['name_sa']} — {step_meta['name_en']}")
        print("#" * 60)

        if step_res:
            print("\n[ANALYSIS OUTPUT]:")
            print(step_res.output)

            if step_res.retrieved_contexts:
                print(f"\n[RETRIEVED RAG EVIDENCE ({len(step_res.retrieved_contexts)} references)]:")
                for c_idx, ctx in enumerate(step_res.retrieved_contexts, 1):
                    sim_str = f" | sim: {ctx.similarity_score}" if ctx.similarity_score else ""
                    print(f"  ({c_idx}) [{ctx.source} - Shloka {ctx.shloka_number or 'Methodology'}{sim_str}]:")
                    preview = ctx.text.replace("\n", " ")[:120]
                    print(f"      \"{preview}...\"")
        else:
            print("[Status]: Step not generated.")

    print("\n" + "=" * 70)
    status_tag = "(Cached)" if result.cached else "(Freshly Generated)"
    print(f"Pipeline finished in {result.execution_time_seconds}s {status_tag}.")
    print("=" * 70)

    if args.save:
        out_file = OUTPUTS_DIR / f"shloka_{target_shloka.shloka_number}_analysis.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json_data = {
                "shloka_id": result.shloka_id,
                "shloka_number": result.shloka_number,
                "shloka_text": result.shloka_text,
                "execution_time_seconds": result.execution_time_seconds,
                "cached": result.cached,
                "steps": {k: v.model_dump() for k, v in result.steps.items()}
            }
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"Saved complete structured output to: {out_file}")

if __name__ == "__main__":
    main()
