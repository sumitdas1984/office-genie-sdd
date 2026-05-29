from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CategoryEnum(str, Enum):
    IT = "IT"
    HR = "HR"
    Payroll = "Payroll"
    Admin = "Admin"
    UNKNOWN = "Unknown"


class RequestStatus(str, Enum):
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ExtractedFields(BaseModel):
    date_mentioned: Optional[str] = None
    system_name: Optional[str] = None
    urgency: str = "medium"
    error_message: Optional[str] = None


class SubmitRequest(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    employee_name: str = Field(..., min_length=1, max_length=100)
    employee_email: EmailStr
    department: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=5000)


class SubmitResponse(BaseModel):
    request_id: str
    status: RequestStatus
    category: CategoryEnum
    subcategory: str
    extracted_fields: ExtractedFields
    suggested_response: str
    routed_to: str
    created_at: datetime