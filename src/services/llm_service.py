"""LLM service for request classification using OpenAI GPT."""

import json
import logging
from typing import Dict, Any

from openai import OpenAI
from pydantic import ValidationError

from src.api.models import LLMResponse
from src.services.config import get_openai_api_key
from src.templates.classification_prompt import render_prompt

logger = logging.getLogger("llm_service")

CATEGORY_MAP = {
    "IT": "IT",
    "HR": "HR",
    "Payroll": "Payroll",
    "Admin": "Admin",
}


def classify_request(message: str, employee_id: str, department: str) -> Dict[str, Any]:
    client = OpenAI(api_key=get_openai_api_key())
    prompt = render_prompt(message=message, employee_id=employee_id, department=department)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a request classification assistant. Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
        validated = LLMResponse(**parsed)
        return {
            "category": validated.category.value,
            "subcategory": validated.subcategory,
            "confidence": validated.confidence,
            "extracted_fields": validated.extracted_fields.model_dump(),
            "suggested_response": validated.suggested_response,
            "routing_target": validated.routing_target,
        }
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning(f"LLM response validation failed: {e}")
        raise ValueError(f"Invalid LLM response: {e}") from e