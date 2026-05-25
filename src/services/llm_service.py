from typing import Any


def classify_request(message: str, employee_id: str, department: str) -> dict[str, Any]:
    """
    Stub for LLM classification. Returns a placeholder response.
    Full implementation in FEATURE-002.
    """
    return {
        "category": "Unknown",
        "subcategory": "needs-review",
        "confidence": 0.0,
        "extracted_fields": {},
        "suggested_response": "Your request has been received and is being reviewed.",
        "routing_target": "unknown-queue",
    }