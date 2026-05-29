import os
from unittest.mock import patch, MagicMock

# Set API key before importing the module
os.environ["OPENAI_API_KEY"] = "sk-test-key"


def test_classify_request_returns_valid_structure():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"category": "IT", "subcategory": "Hardware", "confidence": 0.95, "extracted_fields": {"date_mentioned": null, "system_name": "laptop", "urgency": "medium", "error_message": null}, "suggested_response": "Your request has been received.", "routing_target": "it-support"}'

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