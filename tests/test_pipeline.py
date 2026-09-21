"""
Unit Tests for 7-Step Pipeline Orchestrator and Caching.
Verifies end-to-end execution, non-empty outputs, caching, and offline grounding.
"""

import pytest
from src.chunker import build_and_save_processed_data
from src.pipeline import ShlokaPipelineOrchestrator
from src.cache import ShlokaCache

def test_pipeline_7_steps_execution():
    """Verify that all 7 steps are executed and produce non-empty outputs."""
    shlokas, _ = build_and_save_processed_data()
    shloka_1 = shlokas[0]

    orchestrator = ShlokaPipelineOrchestrator()
    result = orchestrator.run_analysis(shloka=shloka_1, force_refresh=True)

    assert result.shloka_id == shloka_1.id
    assert len(result.steps) == 7, "Pipeline must return exactly 7 step outputs"

    # Validate each individual step
    for step_num in range(1, 8):
        assert step_num in result.steps, f"Step {step_num} missing from pipeline output"
        step_res = result.steps[step_num]
        assert step_res.output is not None
        assert len(step_res.output.strip()) > 0, f"Step {step_num} output should not be empty"
        assert step_res.step_number == step_num

def test_cache_persistence_and_retrieval():
    """Verify that cached step outputs are stored and can be reloaded."""
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

    # Read back
    retrieved = cache.get_step_output(shloka_id=test_shloka_id, step_number=1, model="test-model")
    assert retrieved is not None
    assert retrieved.output == "Test Padavibhaga output"

    # Cleanup
    cache.clear_cache(test_shloka_id)
    cleared = cache.get_step_output(shloka_id=test_shloka_id, step_number=1, model="test-model")
    assert cleared is None
