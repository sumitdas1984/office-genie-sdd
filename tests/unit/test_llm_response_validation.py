import pytest
from src.api.models import LLMResponse

def test_valid_llm_response_passes_validation():
    data = {
        "category": "IT",
        "subcategory": "Hardware",
        "confidence": 0.95,
        "extracted_fields": {"date_mentioned": None, "system_name": "laptop", "urgency": "medium", "error_message": None},
        "suggested_response": "Your request has been received.",
        "routing_target": "it-support"
    }
    result = LLMResponse(**data)
    assert result.category.value == "IT"

def test_confidence_above_1_rejected():
    from pydantic import ValidationError
    data = {
        "category": "IT",
        "subcategory": "Hardware",
        "confidence": 1.5,
        "extracted_fields": {"date_mentioned": None, "system_name": None, "urgency": "medium", "error_message": None},
        "suggested_response": "Test",
        "routing_target": "test"
    }
    with pytest.raises(ValidationError):
        LLMResponse(**data)

def test_invalid_category_rejected():
    from pydantic import ValidationError
    data = {
        "category": "InvalidCategory",
        "subcategory": "Hardware",
        "confidence": 0.5,
        "extracted_fields": {"date_mentioned": None, "system_name": None, "urgency": "medium", "error_message": None},
        "suggested_response": "Test",
        "routing_target": "test"
    }
    with pytest.raises(ValidationError):
        LLMResponse(**data)