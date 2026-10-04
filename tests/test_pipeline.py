"""
Unit Tests for 7-Step Pipeline Orchestrator and Caching.
Verifies end-to-end execution, non-empty outputs, caching, and offline grounding.
"""

import pytest
from src.chunker import build_and_save_processed_data
from src.pipeline import ShlokaPipelineOrchestrator
from src.cache import ShlokaCache

from src.llm import LLMClient

def test_pipeline_7_steps_execution():
    """Verify that all 7 steps are executed, latency is tracked, and outputs are non-empty."""
    shlokas, _ = build_and_save_processed_data()
    shloka_1 = shlokas[0]

    mock_llm = LLMClient(provider="mock")
    orchestrator = ShlokaPipelineOrchestrator(llm_client=mock_llm)
    result = orchestrator.run_analysis(shloka=shloka_1, force_refresh=True)

    assert result.shloka_id == shloka_1.id
    assert len(result.steps) == 7, "Pipeline must return exactly 7 step outputs"
    assert len(result.step_latencies) == 7, "Per-step latencies must be recorded"

    # Validate each individual step
    for step_num in range(1, 8):
        assert step_num in result.steps, f"Step {step_num} missing from pipeline output"
        step_res = result.steps[step_num]
        assert step_res.output is not None
        assert len(step_res.output.strip()) > 0, f"Step {step_num} output should not be empty"
        assert step_res.step_number == step_num
        assert step_res.latency_seconds is not None and step_res.latency_seconds >= 0.0

    # Validate final synthesis
    assert result.final_synthesis is not None, "Final synthesis must be generated after Step 7"
    assert len(result.final_synthesis.content.strip()) > 0, "Final synthesis content cannot be empty"
    assert result.final_synthesis.status in ["fresh", "cached"]
    assert "FINAL EXPLANATION" in result.final_synthesis.content

def test_final_synthesis_prompt_receives_all_inputs():
    """Verify that PromptManager renders all 7 steps, shloka text, and context into synthesis prompt."""
    from src.prompts import PromptManager
    pm = PromptManager()

    shloka_text = "अथातो वातव्याधिदानं व्याख्यास्यामः"
    context = "Specialized Nidana context"
    step_outputs = {
        1: "Step 1 Output Text",
        2: "Step 2 Output Text",
        3: "Step 3 Output Text",
        4: "Step 4 Output Text",
        5: "Step 5 Output Text",
        6: "Step 6 Output Text",
        7: "Step 7 Output Text"
    }

    rendered = pm.render_synthesis_prompt(
        shloka_text=shloka_text,
        retrieved_context=context,
        step_outputs=step_outputs
    )

    assert shloka_text in rendered
    assert context in rendered
    for s_num in range(1, 8):
        assert f"Step {s_num} Output Text" in rendered

def test_cache_persistence_and_retrieval():
    """Verify that cached step outputs and final synthesis are stored and can be reloaded."""
    cache = ShlokaCache()
    test_shloka_id = "test_shloka_099"

    # Write dummy step
    cache.set_step_output(
        shloka_id=test_shloka_id,
        step_number=1,
        step_name_sa="संप्रदानम्",
        step_name_en="Sampradaanam",
        output="Test Padavibhaga output",
        model="test-model"
    )

    # Write final synthesis
    cache.set_final_synthesis(
        shloka_id=test_shloka_id,
        output="Test Final Synthesis output",
        model="test-model"
    )

    # Read back step
    retrieved_step = cache.get_step_output(shloka_id=test_shloka_id, step_number=1, model="test-model")
    assert retrieved_step is not None
    assert retrieved_step.output == "Test Padavibhaga output"

    # Read back synthesis
    retrieved_synth = cache.get_final_synthesis(shloka_id=test_shloka_id, model="test-model")
    assert retrieved_synth is not None
    assert retrieved_synth.content == "Test Final Synthesis output"
    assert retrieved_synth.status == "cached"

    # Cleanup
    cache.clear_cache(test_shloka_id)
    cleared_step = cache.get_step_output(shloka_id=test_shloka_id, step_number=1, model="test-model")
    cleared_synth = cache.get_final_synthesis(shloka_id=test_shloka_id, model="test-model")
    assert cleared_step is None
    assert cleared_synth is None

def test_synthesis_failure_does_not_destroy_step_outputs():
    """Verify that if final synthesis throws an error, steps 1-7 are safely preserved and returned."""
    shlokas, _ = build_and_save_processed_data()
    shloka_1 = shlokas[0]

    class FailingSynthesisLLM(LLMClient):
        def generate(self, prompt: str, system_prompt: str = None) -> str:
            if "final synthesis" in (system_prompt or "").lower() or "final explanation" in (system_prompt or "").lower():
                raise RuntimeError("Simulated Gemini API quota exhaustion during Final Synthesis")
            return super().generate(prompt, system_prompt)

    failing_llm = FailingSynthesisLLM(provider="mock")
    orchestrator = ShlokaPipelineOrchestrator(llm_client=failing_llm)
    result = orchestrator.run_analysis(shloka=shloka_1, force_refresh=True)

    # Verify all 7 steps succeeded and were not lost
    assert len(result.steps) == 7
    for step_num in range(1, 8):
        assert result.steps[step_num].output is not None
        assert len(result.steps[step_num].output) > 0

    # Verify final synthesis provides a graceful fallback explanation
    assert result.final_synthesis is not None
    assert result.final_synthesis.status == "fallback"
    assert "Final synthesis could not be generated" in result.final_synthesis.content

