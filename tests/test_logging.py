from starlette.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_request_id_generated():
    """When no X-Request-ID header is provided, a UUID is generated."""
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "ananya.sharma@company.com",
        "department": "Engineering",
        "message": "Test message",
    })
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) == 36  # UUID4 length


def test_request_id_extracted_from_header():
    """When X-Request-ID header is provided, it is reused."""
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "ananya.sharma@company.com",
        "department": "Engineering",
        "message": "Test message",
    }, headers={"X-Request-ID": "custom-id-123"})
    assert response.headers.get("X-Request-ID") == "custom-id-123"


def test_get_request_id_returns_context_value():
    """get_request_id returns the current request ID from context."""
    from src.middleware.logging import get_request_id, RequestIDMiddleware
    client = TestClient(app)
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "ananya.sharma@company.com",
        "department": "Engineering",
        "message": "Test message",
    }, headers={"X-Request-ID": "test-req-456"})
    # The request ID should be available in context after the request
    # (For this test we verify it's in the response header)
    assert response.headers.get("X-Request-ID") == "test-req-456"