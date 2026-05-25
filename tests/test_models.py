import pytest
from pydantic import ValidationError


class TestSubmitRequestModel:
    """Test Pydantic model validation for submit request."""

    def test_submit_request_valid(self):
        """Valid submission with all required fields."""
        from src.api.models import SubmitRequest
        req = SubmitRequest(
            employee_id="EMP-001",
            employee_name="John Doe",
            employee_email="john.doe@company.com",
            department="Engineering",
            message="My printer is not working",
        )
        assert req.employee_id == "EMP-001"
        assert req.message == "My printer is not working"

    def test_submit_request_email_valid(self):
        """Email field validated as email format."""
        from src.api.models import SubmitRequest
        req = SubmitRequest(
            employee_id="EMP-001",
            employee_name="John Doe",
            employee_email="john.doe@company.com",
            department="Engineering",
            message="Need help",
        )
        assert req.employee_email == "john.doe@company.com"

    def test_submit_request_email_invalid(self):
        """Invalid email format raises ValidationError."""
        from src.api.models import SubmitRequest
        with pytest.raises(ValidationError) as exc_info:
            SubmitRequest(
                employee_id="EMP-001",
                employee_name="John Doe",
                employee_email="not-an-email",
                department="Engineering",
                message="Test",
            )
        assert "employee_email" in str(exc_info.value)

    def test_submit_request_message_required(self):
        """Message field is required and cannot be empty."""
        from src.api.models import SubmitRequest
        with pytest.raises(ValidationError) as exc_info:
            SubmitRequest(
                employee_id="EMP-001",
                employee_name="John Doe",
                employee_email="john@company.com",
                department="Engineering",
                message="",
            )
        assert "message" in str(exc_info.value)


class TestClassificationResponseModel:
    """Test LLM classification response model."""

    def test_classification_response_valid(self):
        """Valid classification with all fields."""
        from src.api.models import ClassificationResponse
        resp = ClassificationResponse(
            category="IT",
            subcategory="Hardware",
            confidence=0.95,
            extracted_fields={"urgency": "medium"},
            suggested_response="Your printer request has been forwarded to IT.",
            routing_target="it-hardware-queue",
        )
        assert resp.category == "IT"
        assert resp.subcategory == "Hardware"
        assert resp.confidence == 0.95

    def test_classification_category_enum(self):
        """Category must be one of IT, HR, Payroll, Admin."""
        from src.api.models import ClassificationResponse, CategoryEnum
        resp = ClassificationResponse(
            category=CategoryEnum.IT,
            subcategory="Software",
            confidence=0.85,
            extracted_fields={},
            suggested_response="",
            routing_target="it-software-queue",
        )
        assert resp.category == CategoryEnum.IT

    def test_classification_confidence_range(self):
        """Confidence must be between 0 and 1."""
        from src.api.models import ClassificationResponse
        with pytest.raises(ValidationError):
            ClassificationResponse(
                category="IT",
                subcategory="Software",
                confidence=1.5,
                extracted_fields={},
                suggested_response="",
                routing_target="it-software-queue",
            )


class TestSubmitResponseModel:
    """Test submit endpoint response model."""

    def test_submit_response_success(self):
        """Success response includes all fields."""
        from src.api.models import SubmitResponse, RequestStatus, CategoryEnum, ExtractedFields
        from datetime import datetime, timezone
        resp = SubmitResponse(
            request_id="REQ-2026-0023",
            status=RequestStatus.ACKNOWLEDGED,
            category=CategoryEnum.IT,
            subcategory="Hardware",
            extracted_fields=ExtractedFields(urgency="low"),
            suggested_response="Your request is being processed.",
            routed_to="it-hardware-queue",
            created_at=datetime.now(timezone.utc),
        )
        assert resp.request_id == "REQ-2026-0023"
        assert resp.status == RequestStatus.ACKNOWLEDGED
        assert resp.category == CategoryEnum.IT


class TestRequestStatusModel:
    """Test request status enum and transitions."""

    def test_status_enum_values(self):
        """Status enum has correct values."""
        from src.api.models import RequestStatus
        assert RequestStatus.ACKNOWLEDGED.value == "acknowledged"
        assert RequestStatus.IN_PROGRESS.value == "in-progress"
        assert RequestStatus.RESOLVED.value == "resolved"
        assert RequestStatus.CLOSED.value == "closed"

    def test_status_update_valid_transition(self):
        """Valid transitions: acknowledged->in-progress->resolved->closed."""
        from src.api.models import RequestStatusUpdate, RequestStatus
        update = RequestStatusUpdate(status="in-progress")
        assert update.status == RequestStatus.IN_PROGRESS