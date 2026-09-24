"""
7-Step Shloka Analysis Pipeline Orchestrator.
Sequentially executes the seven Ayurvidya steps:
1. संप्रदानम् (Sampradaanam)
2. पदविभागः (Padavibhaga)
3. अन्वयः (Anwaya)
4. अन्वयार्थः (Anwayartha)
5. भावार्थः (Bhavartha)
6. पदकृत्यम् (Padakrutyam)
7. ध्वनितार्थः (Dhvanitartha)
Incorporates step-specific RAG retrieval, context chaining, caching, and latency tracking.
"""

import time
from typing import Dict, Any, Optional, Callable
from src.config import DEBUG_MODE
from src.schemas import ShlokaData, StepOutput, PipelineResult, RetrievalResult
from src.prompts import PromptManager, STEPS_CONFIG
from src.retriever import ShlokaRetriever
from src.llm import LLMClient
from src.cache import ShlokaCache

def safe_log(msg: str):
    """Safely log messages to stdout without crashing on Windows charmap encoding limitations."""
    try:
        print(msg)
    except Exception:
        try:
            print(msg.encode("ascii", "replace").decode("ascii"))
        except Exception:
            pass

class ShlokaPipelineOrchestrator:
    """Orchestrates step-specific retrieval, cascading context, and LLM reasoning across 7 steps."""

    def __init__(
        self,
        retriever: Optional[ShlokaRetriever] = None,
        llm_client: Optional[LLMClient] = None,
        prompt_manager: Optional[PromptManager] = None,
        cache: Optional[ShlokaCache] = None
    ):
        self.retriever = retriever or ShlokaRetriever()
        self._explicit_llm = llm_client is not None
        self.llm_client = llm_client or LLMClient()
        self.prompt_manager = prompt_manager or PromptManager()
        self.cache = cache or ShlokaCache()

    def run_analysis(
        self,
        shloka: ShlokaData,
        force_refresh: bool = False,
        progress_callback: Optional[Callable[[int, str, str], None]] = None
    ) -> PipelineResult:
        """
        Executes the full 7-step analysis on a given Shloka.
        Checks cache first. If any step is missing or force_refresh=True, computes it via RAG + LLM.
        """
        start_time = time.time()
        shloka_id = shloka.id
        shloka_num = shloka.shloka_number
        shloka_text = shloka.text

        # Synchronize LLMClient with active environment only if not explicitly injected
        if not self._explicit_llm:
            from src.config import get_active_llm_config
            active_provider, active_model, active_key = get_active_llm_config()
            if (self.llm_client.provider != active_provider or 
                self.llm_client.model != active_model or 
                self.llm_client.api_key != active_key):
                self.llm_client = LLMClient(provider=active_provider, model=active_model, api_key=active_key)

        if DEBUG_MODE:
            safe_log("\n" + "#"*60)
            safe_log(f"[Pipeline] Starting 7-Step Analysis for: {shloka_id} (Shloka {shloka.shloka_number_display})")
            safe_log("#"*60)

        # 1. Check cache for all steps
        cached_steps: Dict[int, StepOutput] = {}
        if not force_refresh:
            cached_steps = self.cache.get_all_steps(shloka_id=shloka_id, model=self.llm_client.model)
            if len(cached_steps) == 7:
                safe_log(
                    f"[DEBUG LOG] shloka_id={shloka_id} | provider={self.llm_client.provider} | "
                    f"model={self.llm_client.model} | is_mock={self.llm_client.is_mock} | "
                    f"cache_used=True | backend_called=cache"
                )
                if DEBUG_MODE:
                    print(f"[Pipeline] Cache hit! Loaded all 7 steps for {shloka_id} from local cache.")
                return PipelineResult(
                    shloka_id=shloka_id,
                    shloka_number=shloka_num,
                    shloka_text=shloka_text,
                    steps=cached_steps,
                    execution_time_seconds=round(time.time() - start_time, 2),
                    cached=True
                )

        backend_name = "mock" if self.llm_client.is_mock else self.llm_client.provider
        safe_log(
            f"[DEBUG LOG] shloka_id={shloka_id} | provider={self.llm_client.provider} | "
            f"model={self.llm_client.model} | is_mock={self.llm_client.is_mock} | "
            f"cache_used=False | backend_called={backend_name}"
        )

        steps_result: Dict[int, StepOutput] = dict(cached_steps)
        previous_text_outputs: Dict[int, str] = {k: v.output for k, v in cached_steps.items()}
        step_latencies: Dict[int, float] = {}

        # 2. Iterate through Step 1 to 7 sequentially
        for step_num in range(1, 8):
            step_start = time.time()
            step_meta = STEPS_CONFIG[step_num]
            step_name_sa = step_meta["name_sa"]
            step_name_en = step_meta["name_en"]

            # If this step is already in cache and we aren't forcing refresh, skip computing
            if step_num in steps_result and not force_refresh:
                if progress_callback:
                    progress_callback(step_num, step_name_sa, "Loaded from cache")
                continue

            if progress_callback:
                progress_callback(step_num, step_name_sa, "Retrieving context & generating...")

            if DEBUG_MODE:
                safe_log(f"\n---> Executing Step {step_num}: {step_name_sa} ({step_name_en})")

            # Step-aware Retrieval from Vector DB
            retrieved_chunks = self.retriever.retrieve_for_step(
                step_number=step_num,
                shloka_text=shloka_text,
                shloka_number=shloka_num,
                top_k=4
            )

            # Format retrieved context string
            context_pieces = []
            for idx, r in enumerate(retrieved_chunks, 1):
                dist_str = f" [score: {r.similarity_score}]" if r.similarity_score is not None else ""
                context_pieces.append(f"[{idx}] Source: {r.source} (Shloka {r.shloka_number or 'N/A'}{dist_str}):\n{r.text}")

            context_str = "\n\n".join(context_pieces) if context_pieces else "Context not available in local knowledge store."

            # Render step prompt with injected previous outputs and retrieved context
            rendered_prompt = self.prompt_manager.render_prompt(
                step_number=step_num,
                shloka_text=shloka_text,
                retrieved_context=context_str,
                previous_outputs=previous_text_outputs
            )

            # System prompt identifying the step with strict grounding directive
            sys_instruction = (
                f"You are a strict Sanskrit & Ayurveda analytical assistant executing Step {step_num}: "
                f"{step_name_sa} ({step_name_en}) following the Ayurvidya Prabhashanam methodology. "
                "You must base your analysis strictly on the supplied ORIGINAL SHLOKA and RETRIEVED CONTEXT. "
                "Never invent, hallucinate, or extrapolate facts, grammatical attributes, roots, etymologies, "
                "or textual claims not directly attested in the provided context."
            )

            # LLM Generation
            step_output_text = self.llm_client.generate(prompt=rendered_prompt, system_prompt=sys_instruction)
            step_duration = round(time.time() - step_start, 2)
            step_latencies[step_num] = step_duration

            # Build step output object
            step_res = StepOutput(
                step_number=step_num,
                step_name_sanskrit=step_name_sa,
                step_name_english=step_name_en,
                output=step_output_text,
                retrieved_contexts=retrieved_chunks,
                model=self.llm_client.model,
                latency_seconds=step_duration
            )

            # Update working records
            steps_result[step_num] = step_res
            previous_text_outputs[step_num] = step_output_text

            # Save step output to cache
            self.cache.set_step_output(
                shloka_id=shloka_id,
                step_number=step_num,
                step_name_sa=step_name_sa,
                step_name_en=step_name_en,
                output=step_output_text,
                model=self.llm_client.model,
                retrieved_contexts=retrieved_chunks
            )

        total_time = round(time.time() - start_time, 2)
        if DEBUG_MODE:
            safe_log(f"\n[Pipeline] Completed 7 steps in {total_time} seconds. Latencies: {step_latencies}")

        return PipelineResult(
            shloka_id=shloka_id,
            shloka_number=shloka_num,
            shloka_text=shloka_text,
            steps=steps_result,
            execution_time_seconds=total_time,
            step_latencies=step_latencies,
            cached=False
        )
