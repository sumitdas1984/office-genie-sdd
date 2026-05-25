from starlette.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_submit_valid_request():
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "ananya.sharma@company.com",
        "department": "Engineering",
        "message": "I can't access my payslip for June.",
    })
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["request_id"].startswith("REQ-")
    assert data["status"] == "acknowledged"


def test_submit_invalid_request_missing_field():
    response = client.post("/api/submit", json={"employee_id": "EMP-0042"})
    assert response.status_code == 422


def test_submit_invalid_email():
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "not-an-email",
        "department": "Engineering",
        "message": "Test",
    })
    assert response.status_code == 422


def test_submit_response_has_all_required_fields():
    """Verify the response contains all required fields."""
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "ananya.sharma@company.com",
        "department": "Engineering",
        "message": "I can't access my payslip for June.",
    })
    assert response.status_code == 200
    data = response.json()
    required_fields = ["request_id", "status", "category", "subcategory",
                      "extracted_fields", "suggested_response", "routed_to", "created_at"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


def test_request_id_uniqueness():
    """Verify that each request gets a unique ID."""
    ids = set()
    for _ in range(5):
        response = client.post("/api/submit", json={
            "employee_id": "EMP-0042",
            "employee_name": "Ananya Sharma",
            "employee_email": "ananya.sharma@company.com",
            "department": "Engineering",
            "message": "Test",
        })
        assert response.status_code == 200
        ids.add(response.json()["request_id"])
    assert len(ids) == 5, "Request IDs must be unique"


def test_empty_message_rejected():
    """Empty message string returns 422."""
    response = client.post("/api/submit", json={
        "employee_id": "EMP-0042",
        "employee_name": "Ananya Sharma",
        "employee_email": "ananya.sharma@company.com",
        "department": "Engineering",
        "message": "",
    })
    assert response.status_code == 422