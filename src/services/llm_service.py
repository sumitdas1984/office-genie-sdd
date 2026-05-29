"""Stub LLM service. Full implementation in FEATURE-002."""

from src.api.models import CategoryEnum


def classify_request(message: str, employee_id: str, department: str) -> dict:
    return {
        "category": CategoryEnum.UNKNOWN,
        "subcategory": "pending",
        "confidence": 0.0,
        "extracted_fields": {
            "date_mentioned": None,
            "system_name": None,
            "urgency": "medium",
            "error_message": None,
        },
        "suggested_response": "Your request has been received and is being reviewed.",
        "routing_target": "unassigned",
    }