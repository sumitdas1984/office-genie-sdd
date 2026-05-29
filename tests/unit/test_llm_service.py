import os
import json
from unittest.mock import patch, MagicMock

os.environ["OPENAI_API_KEY"] = "sk-test-key"


def _make_mock_response(category, subcategory, confidence, extracted_fields, suggested_response, routing_target):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "category": category,
        "subcategory": subcategory,
        "confidence": confidence,
        "extracted_fields": extracted_fields,
        "suggested_response": suggested_response,
        "routing_target": routing_target,
    })
    return mock_response


def test_timeout_raises_and_retries():
    """LLM retries on timeout and succeeds on 3rd attempt."""
    mock_success = _make_mock_response(
        category="IT", subcategory="Hardware", confidence=0.9,
        extracted_fields={"date_mentioned": None, "system_name": None, "urgency": "medium", "error_message": None},
        suggested_response="ok", routing_target="it"
    )

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            Exception("Connection timeout"),
            Exception("Connection timeout"),
            mock_success,
        ]
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        result = classify_request("test", "EMP-001", "Engineering")

    assert result["category"] == "IT"


def test_confidence_zero_passes_validation():
    """Confidence of 0.0 is valid and passes Pydantic validation."""
    mock_response = _make_mock_response(
        category="IT", subcategory="Hardware", confidence=0.0,
        extracted_fields={"date_mentioned": None, "system_name": None, "urgency": "medium", "error_message": None},
        suggested_response="ok", routing_target="it"
    )

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        result = classify_request("test", "EMP-001", "Engineering")

    assert result["confidence"] == 0.0


def test_hr_category_classification():
    """HR category is correctly classified with Leave subcategory."""
    mock_response = _make_mock_response(
        category="HR", subcategory="Leave", confidence=0.88,
        extracted_fields={"date_mentioned": "2026-06-15", "system_name": None, "urgency": "high", "error_message": None},
        suggested_response="Leave request noted.", routing_target="hr-team"
    )

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        result = classify_request("I want to take leave on June 15", "EMP-001", "HR")

    assert result["category"] == "HR"
    assert result["subcategory"] == "Leave"
    assert result["extracted_fields"]["date_mentioned"] == "2026-06-15"


def test_payroll_category_classification():
    """Payroll category is correctly classified with Deductions subcategory."""
    mock_response = _make_mock_response(
        category="Payroll", subcategory="Deductions", confidence=0.92,
        extracted_fields={"date_mentioned": None, "system_name": None, "urgency": "medium", "error_message": None},
        suggested_response="Payroll inquiry received.", routing_target="payroll-team"
    )

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        result = classify_request("My payslip shows wrong deductions", "EMP-001", "Finance")

    assert result["category"] == "Payroll"
    assert result["subcategory"] == "Deductions"


def test_admin_category_classification():
    """Admin category is correctly classified with Facilities subcategory."""
    mock_response = _make_mock_response(
        category="Admin", subcategory="Facilities", confidence=0.85,
        extracted_fields={"date_mentioned": None, "system_name": None, "urgency": "low", "error_message": None},
        suggested_response="Facilities request noted.", routing_target="facilities-team"
    )

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        result = classify_request("The projector in room 301 is not working", "EMP-001", "Sales")

    assert result["category"] == "Admin"
    assert result["subcategory"] == "Facilities"


def test_classify_request_returns_valid_structure():
    mock_response = _make_mock_response(
        category="IT", subcategory="Hardware", confidence=0.95,
        extracted_fields={"date_mentioned": None, "system_name": "laptop", "urgency": "medium", "error_message": None},
        suggested_response="Your request has been received.", routing_target="it-support"
    )

    with patch("src.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.llm_service import classify_request
        result = classify_request("My laptop screen flickers", "EMP-001", "Engineering")

    assert result["category"] == "IT"
    assert result["subcategory"] == "Hardware"
    assert result["confidence"] == 0.95
    assert "extracted_fields" in result
    assert "suggested_response" in result
    assert "routing_target" in result