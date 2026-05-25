import pytest
from pydantic import ValidationError


class TestSubmitRequestModel:
    """Test Pydantic model validation for submit request."""

    def test_submit_request_valid_minimal(self):
        """Minimal valid submission requires only text."""
        from src.api.models import SubmitRequest
        req = SubmitRequest(text="My printer is not working")
        assert req.text == "My printer is not working"

    def test_submit_request_with_email(self):
        """Email field validated as email format."""
        from src.api.models import SubmitRequest
        req = SubmitRequest(text="Need help with password", email="employee@company.com")
        assert req.email == "employee@company.com"

    def test_submit_request_email_invalid(self):
        """Invalid email format raises ValidationError."""
        from src.api.models import SubmitRequest
        with pytest.raises(ValidationError) as exc_info:
            SubmitRequest(text="Test", email="not-an-email")
        assert "email" in str(exc_info.value)

    def test_submit_request_text_required(self):
        """Text field is required."""
        from src.api.models import SubmitRequest
        with pytest.raises(ValidationError) as exc_info:
            SubmitRequest(text="")
        assert "text" in str(exc_info.value)


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
        """Success response includes request_id and classification."""
        from src.api.models import SubmitResponse, ClassificationResponse, RequestStatus
        resp = SubmitResponse(
            request_id="REQ-2026-0023",
            status=RequestStatus.ACKNOWLEDGED,
            classification=ClassificationResponse(
                category="IT",
                subcategory="Hardware",
                confidence=0.9,
                extracted_fields={"urgency": "low"},
                suggested_response="Your request is being processed.",
                routing_target="it-hardware-queue",
            ),
        )
        assert resp.request_id == "REQ-2026-0023"
        assert resp.status == RequestStatus.ACKNOWLEDGED
        assert resp.classification.category == "IT"


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