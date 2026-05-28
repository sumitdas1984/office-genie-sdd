import os
from jinja2 import Environment, FileSystemLoader


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


def get_jinja_env() -> Environment:
    """Get Jinja2 environment with template directory."""
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    return Environment(loader=FileSystemLoader(template_dir))


def render_classification_prompt(
    message: str,
    employee_id: str,
    department: str,
) -> str:
    """
    Render the classification prompt template with given variables.
    """
    env = get_jinja_env()
    template = env.get_template("classification_prompt.j2")
    return template.render(
        message=message,
        employee_id=employee_id,
        department=department,
    )


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