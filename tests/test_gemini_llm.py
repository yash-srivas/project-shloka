"""
Unit tests for Gemini LLM provider integration with google-genai SDK.
Verifies provider selection, API key safety (no logging), and mock fallback.
"""

import io
import sys
import pytest
from unittest.mock import patch, MagicMock
from src.llm import LLMClient

def test_gemini_provider_selection_with_key():
    """Verify provider=gemini with an api_key sets provider to gemini and is_mock to False."""
    client = LLMClient(provider="gemini", model="gemini-1.5-flash", api_key="AIzaSyTestFakeKey123")
    assert client.provider == "gemini"
    assert client.model == "gemini-1.5-flash"
    assert client.is_mock is False

def test_gemini_provider_fallback_when_no_key():
    """Verify provider=gemini without an API key safely falls back to mock mode."""
    client = LLMClient(provider="gemini", model="gemini-1.5-flash", api_key="")
    assert client.is_mock is True
    # Should generate mock response without error
    out = client.generate("Test prompt")
    assert len(out) > 0

def test_no_api_key_printed_or_logged(capsys):
    """Verify that even on error, the secret API key is never printed or logged."""
    fake_secret_key = "SECRET_GEMINI_KEY_DO_NOT_LEAK_9999"
    client = LLMClient(provider="gemini", model="gemini-1.5-flash", api_key=fake_secret_key)
    
    # Intentionally trigger error by passing an invalid call
    with patch("google.genai.Client") as mock_genai_cls:
        mock_instance = MagicMock()
        mock_instance.models.generate_content.side_effect = Exception(
            f"Authentication failed with key {fake_secret_key}: invalid credential"
        )
        mock_genai_cls.return_value = mock_instance
        
        response = client.generate(prompt="What is Vata?")
        
        # Verify fallback response was generated
        assert response is not None
        assert len(response) > 0

    captured = capsys.readouterr()
    # Ensure the secret key NEVER appears in stdout or stderr
    assert fake_secret_key not in captured.out
    assert fake_secret_key not in captured.err

def test_gemini_passes_system_instruction_and_temperature():
    """Verify that system_instruction and temperature=0.2 are passed to GenerateContentConfig."""
    client = LLMClient(provider="gemini", model="gemini-1.5-flash", api_key="test_key")
    
    with patch("google.genai.Client") as mock_genai_cls:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Grounded Sanskrit analysis from real Gemini."
        mock_instance.models.generate_content.return_value = mock_response
        mock_genai_cls.return_value = mock_instance
        
        result = client.generate(
            prompt="Analyze Shloka 1",
            system_prompt="You are an expert Ayurveda scholar."
        )
        
        assert result == "Grounded Sanskrit analysis from real Gemini."
        mock_instance.models.generate_content.assert_called_once()
        call_kwargs = mock_instance.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-1.5-flash"
        assert call_kwargs["contents"] == "Analyze Shloka 1"
        assert call_kwargs["config"].temperature == 0.2
        assert call_kwargs["config"].system_instruction == "You are an expert Ayurveda scholar."
