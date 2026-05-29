"""LLM service for request classification using OpenAI GPT."""

import json
import logging
import time
from typing import Dict, Any

from openai import OpenAI
from pydantic import ValidationError

from src.api.models import LLMResponse
from src.services.config import get_openai_api_key
from src.templates.classification_prompt import render_prompt

logger = logging.getLogger("llm_service")


def _classify_with_retry(message: str, employee_id: str, department: str, max_retries: int = 3) -> Dict[str, Any]:
    """Internal classification with exponential backoff retry."""
    client = OpenAI(api_key=get_openai_api_key())
    prompt = render_prompt(message=message, employee_id=employee_id, department=department)

    last_error = None
    for attempt in range(max_retries):
        try:
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

        except Exception as e:
            last_error = e
            error_str = str(e).lower()

            if "401" in error_str or "403" in error_str or "auth" in error_str:
                logger.error(f"OpenAI auth error (not retrying): {e}")
                raise

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"LLM call failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

    raise last_error


def classify_request(message: str, employee_id: str, department: str) -> Dict[str, Any]:
    return _classify_with_retry(message, employee_id, department)


def classify_request_fallback(message: str, employee_id: str, department: str) -> Dict[str, Any]:
    """Fallback classification when LLM is unavailable."""
    logger.warning("Using fallback classification — LLM unavailable")
    return {
        "category": "Unknown",
        "subcategory": "needs-review",
        "confidence": 0.0,
        "extracted_fields": {
            "date_mentioned": None,
            "system_name": None,
            "urgency": "medium",
            "error_message": None,
        },
        "suggested_response": "Your request has been received and is being reviewed by our team.",
        "routing_target": "unassigned",
    }