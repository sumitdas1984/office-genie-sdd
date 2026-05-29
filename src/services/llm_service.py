"""LLM service for request classification using OpenAI GPT."""

import json
import logging
from typing import Dict, Any

from openai import OpenAI

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
    result = json.loads(content)

    category = result.get("category", "Unknown")
    if category not in CATEGORY_MAP:
        category = "Unknown"

    return {
        "category": category,
        "subcategory": result.get("subcategory", "needs-review"),
        "confidence": float(result.get("confidence", 0.0)),
        "extracted_fields": {
            "date_mentioned": result.get("extracted_fields", {}).get("date_mentioned"),
            "system_name": result.get("extracted_fields", {}).get("system_name"),
            "urgency": result.get("extracted_fields", {}).get("urgency", "medium"),
            "error_message": result.get("extracted_fields", {}).get("error_message"),
        },
        "suggested_response": result.get("suggested_response", "Your request has been received and is being reviewed."),
        "routing_target": result.get("routing_target", "unassigned"),
    }