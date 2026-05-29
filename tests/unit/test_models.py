import pytest
from enum import Enum


class TestCategoryEnum:
    def test_category_values(self):
        from src.api.models import CategoryEnum
        members = [e.value for e in CategoryEnum]
        assert "IT" in members
        assert "HR" in members
        assert "Payroll" in members
        assert "Admin" in members


class TestRequestStatus:
    def test_status_values(self):
        from src.api.models import RequestStatus
        members = [e.value for e in RequestStatus]
        assert "acknowledged" in members
        assert "in-progress" in members
        assert "resolved" in members
        assert "closed" in members


class TestExtractedFields:
    def test_defaults(self):
        from src.api.models import ExtractedFields
        f = ExtractedFields()
        assert f.date_mentioned is None
        assert f.system_name is None
        assert f.urgency == "medium"
        assert f.error_message is None