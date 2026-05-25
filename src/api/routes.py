from datetime import datetime, timezone

from fastapi import APIRouter, status

from src.api.models import CategoryEnum, SubmitRequest, SubmitResponse
from src.services.id_generator import generate_request_id
from src.services.llm_service import classify_request
from src.services.routing_service import route_request

router = APIRouter(prefix="/api", tags=["Requests"])


def _to_category(value: str) -> CategoryEnum:
    try:
        return CategoryEnum(value)
    except ValueError:
        return CategoryEnum.IT


@router.post("/submit", response_model=SubmitResponse, status_code=status.HTTP_200_OK)
def submit_request(request: SubmitRequest) -> SubmitResponse:
    request_id = generate_request_id()

    classification = classify_request(
        message=request.message,
        employee_id=request.employee_id,
        department=request.department,
    )

    routing = route_request(
        category=classification["category"],
        subcategory=classification["subcategory"],
        urgency=classification["extracted_fields"].get("urgency", "medium"),
    )

    return SubmitResponse(
        request_id=request_id,
        status="acknowledged",
        category=_to_category(classification["category"]),
        subcategory=classification["subcategory"],
        extracted_fields=classification["extracted_fields"],
        suggested_response=classification["suggested_response"],
        routed_to=routing["routing_target"],
        created_at=datetime.now(timezone.utc),
    )