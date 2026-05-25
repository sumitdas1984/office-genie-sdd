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