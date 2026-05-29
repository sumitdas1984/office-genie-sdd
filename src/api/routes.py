import logging
from datetime import datetime, timezone

from fastapi import APIRouter, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import Response

from src.api.models import (
    ExtractedFields,
    RequestStatus,
    SubmitRequest,
    SubmitResponse,
)
from src.middleware.logging import get_request_id
from src.services.config import ConfigError
from src.services.id_generator import generate_request_id
from src.services.llm_service import classify_request, classify_request_fallback
from src.services.routing_service import route_request

router = APIRouter()
logger = logging.getLogger("api")


@router.post("/api/submit", response_model=SubmitResponse)
def submit_request(request: SubmitRequest, response: Response) -> SubmitResponse:
    request_id = generate_request_id()

    logger.info(
        "validation_passed",
        extra={
            "event": "validation_passed",
            "request_id": request_id,
            "duration_ms": None,
        },
    )

    try:
        llm_result = classify_request(
            message=request.message,
            employee_id=request.employee_id,
            department=request.department,
        )
    except ConfigError:
        logger.warning(f"OpenAI API key not configured, using fallback classification")
        llm_result = classify_request_fallback(
            message=request.message,
            employee_id=request.employee_id,
            department=request.department,
        )
    except Exception as e:
        logger.warning(f"LLM classification failed: {e}, using fallback")
        llm_result = classify_request_fallback(
            message=request.message,
            employee_id=request.employee_id,
            department=request.department,
        )

    routing_target = route_request(
        category=llm_result["category"],
        subcategory=llm_result["subcategory"],
        extracted_fields=llm_result["extracted_fields"],
    )

    logger.info(
        "response_sent",
        extra={
            "event": "response_sent",
            "request_id": request_id,
            "category": llm_result["category"],
            "routing_target": routing_target,
            "duration_ms": None,
        },
    )

    response.headers["X-Request-ID"] = get_request_id()

    return SubmitResponse(
        request_id=request_id,
        status=RequestStatus.ACKNOWLEDGED,
        category=llm_result["category"],
        subcategory=llm_result["subcategory"],
        extracted_fields=ExtractedFields(**llm_result["extracted_fields"]),
        suggested_response=llm_result["suggested_response"],
        routed_to=routing_target,
        created_at=datetime.now(timezone.utc),
    )