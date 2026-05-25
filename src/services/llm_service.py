import os


class ConfigError(Exception):
    """Raised when required configuration is missing."""
    pass


def load_api_key() -> str:
    """
    Load and validate OPENAI_API_KEY from environment.
    Raises ConfigError if not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigError("OPENAI_API_KEY environment variable is not set")
    return api_key


def classify_request(message: str, employee_id: str, department: str) -> dict:
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