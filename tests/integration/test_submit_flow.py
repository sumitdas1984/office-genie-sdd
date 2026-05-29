import pytest
import uuid


class TestSubmitFlow:
    def test_happy_path_submission(self, client):
        response = client.post(
            "/api/submit",
            json={
                "employee_id": "EMP-042",
                "employee_name": "Ananya Sharma",
                "employee_email": "ananya@company.com",
                "department": "Engineering",
                "message": "My laptop screen flickers when I plug in the charger",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["request_id"].startswith("REQ-")
        assert data["status"] == "acknowledged"
        assert "category" in data
        assert "subcategory" in data
        assert "extracted_fields" in data
        assert "suggested_response" in data
        assert "routed_to" in data
        assert "created_at" in data
        assert "x-request-id" in response.headers

    def test_validation_rejects_missing_fields(self, client):
        response = client.post(
            "/api/submit",
            json={
                "employee_id": "EMP-001",
            },
        )
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert len(errors) >= 4

    def test_validation_rejects_invalid_email(self, client):
        response = client.post(
            "/api/submit",
            json={
                "employee_id": "EMP-001",
                "employee_name": "John Doe",
                "employee_email": "not-an-email",
                "department": "Engineering",
                "message": "Test message",
            },
        )
        assert response.status_code == 422

    def test_validation_rejects_empty_message(self, client):
        response = client.post(
            "/api/submit",
            json={
                "employee_id": "EMP-001",
                "employee_name": "John Doe",
                "employee_email": "john@company.com",
                "department": "Engineering",
                "message": "",
            },
        )
        assert response.status_code == 422

    def test_request_id_header_is_uuid4(self, client):
        response = client.post(
            "/api/submit",
            json={
                "employee_id": "EMP-001",
                "employee_name": "John Doe",
                "employee_email": "john@company.com",
                "department": "Engineering",
                "message": "Test",
            },
        )
        import uuid
        uid = response.headers["x-request-id"]
        uuid.UUID(uid)

    def test_request_id_preserved_if_provided(self, client):
        custom_id = str(uuid.uuid4())
        response = client.post(
            "/api/submit",
            headers={"x-request-id": custom_id},
            json={
                "employee_id": "EMP-001",
                "employee_name": "John Doe",
                "employee_email": "john@company.com",
                "department": "Engineering",
                "message": "Test",
            },
        )
        assert response.headers["x-request-id"] == custom_id

    def test_health_endpoint_always_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_created_at_is_iso_format(self, client):
        response = client.post(
            "/api/submit",
            json={
                "employee_id": "EMP-001",
                "employee_name": "John Doe",
                "employee_email": "john@company.com",
                "department": "Engineering",
                "message": "Test",
            },
        )
        from datetime import datetime
        data = response.json()
        dt = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        assert dt is not None

    def test_message_max_length(self, client):
        long_message = "x" * 5001
        response = client.post(
            "/api/submit",
            json={
                "employee_id": "EMP-001",
                "employee_name": "John Doe",
                "employee_email": "john@company.com",
                "department": "Engineering",
                "message": long_message,
            },
        )
        assert response.status_code == 422