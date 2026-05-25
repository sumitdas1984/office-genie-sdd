from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class CategoryEnum(str, Enum):
    IT = "IT"
    HR = "HR"
    PAYROLL = "Payroll"
    ADMIN = "Admin"


class ExtractedFields(BaseModel):
    date_mentioned: Optional[str] = None
    system_name: Optional[str] = None
    urgency: Optional[str] = None
    error_message: Optional[str] = None


class SubmitRequest(BaseModel):
    employee_id: str = Field(..., min_length=1)
    employee_name: str = Field(..., min_length=1)
    employee_email: EmailStr
    department: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ClassificationResponse(BaseModel):
    category: CategoryEnum
    subcategory: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    extracted_fields: ExtractedFields = Field(default_factory=ExtractedFields)
    suggested_response: str
    routing_target: str


class RequestStatus(str, Enum):
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SubmitResponse(BaseModel):
    request_id: str
    status: RequestStatus
    category: CategoryEnum
    subcategory: str
    extracted_fields: ExtractedFields
    suggested_response: str
    routed_to: str
    created_at: datetime


class RequestStatusUpdate(BaseModel):
    status: RequestStatus

    @field_validator("status")
    @classmethod
    def validate_status_transition(cls, v: RequestStatus) -> RequestStatus:
        return v