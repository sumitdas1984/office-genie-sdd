from starlette.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_validation_error_returns_422_with_details():
    """Validation failure returns 422 with error details."""
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        # missing all other required fields
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_message_too_long_returns_422():
    """Message exceeding 5000 chars returns 422."""
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "ananya.sharma@company.com",
        "department": "Engineering",
        "message": "x" * 5001,  # exceeds 5000 char limit
    })
    assert response.status_code == 422


def test_invalid_email_returns_422():
    """Invalid email format returns 422."""
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "not-an-email",
        "department": "Engineering",
        "message": "Test message",
    })
    assert response.status_code == 422