import os
import json
import time
from unittest.mock import patch, MagicMock

os.environ["OPENAI_API_KEY"] = "sk-test-key"


def test_retry_on_transient_error():
    """LLM retries on transient errors and succeeds on 3rd attempt."""
    call_count = 0

    def make_mock_response(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Network error")
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message.content = '{"category": "IT", "subcategory": "Hardware", "confidence": 0.9, "extracted_fields": {"date_mentioned": null, "system_name": null, "urgency": "medium", "error_message": null}, "suggested_response": "ok", "routing_target": "it"}'
        return mock_resp

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = make_mock_response
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        result = classify_request("test", "EMP-001", "Engineering")

    assert call_count == 3, f"Expected 3 calls, got {call_count}"
    assert result["category"] == "IT"


def test_auth_error_fails_immediately():
    """Auth errors (401/403) fail immediately without retry."""
    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("401 Unauthorized")
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        try:
            classify_request("test", "EMP-001", "Engineering")
            assert False, "Should have raised"
        except Exception as e:
            assert "401" in str(e) or "auth" in str(e).lower()


def test_fallback_on_final_failure():
    """After all retries exhausted, fallback returns Unknown category with 0.0 confidence."""
    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("All retries failed")
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request_fallback
        result = classify_request_fallback("test", "EMP-001", "Engineering")

    assert result["category"] == "Unknown"
    assert result["subcategory"] == "needs-review"
    assert result["confidence"] == 0.0


def test_malformed_json_raises():
    """Malformed JSON in LLM response raises ValueError."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "not valid json {{{"

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        try:
            classify_request("test", "EMP-001", "Engineering")
            assert False, "Should raise"
        except (json.JSONDecodeError, ValueError):
            pass  # Expected


def test_confidence_zero_passes_validation():
    """Confidence of 0.0 is valid and passes Pydantic validation."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"category": "IT", "subcategory": "Hardware", "confidence": 0.0, "extracted_fields": {"date_mentioned": null, "system_name": null, "urgency": "medium", "error_message": null}, "suggested_response": "ok", "routing_target": "it"}'

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        result = classify_request("test", "EMP-001", "Engineering")

    assert result["confidence"] == 0.0